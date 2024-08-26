import re
import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

# Função para limpar e converter dados


def clean_column(df, column_name):
    df[column_name] = df[column_name].astype(str)
    df[column_name] = df[column_name].str.replace(r'[()]*', '', regex=True)
    df[column_name] = df[column_name].str.replace(',', '.', regex=False)
    df[column_name] = pd.to_numeric(df[column_name], errors='coerce')
    return df


# Defina o caminho dos arquivos Excel/CSV aqui
file_path1 = "./data/eleitorado_local_votacao_2020_geografica.xls"
file_path2 = "./data/votação_secão_2020 vereador.csv"


# Leitura dos arquivos
df1 = pd.read_excel(file_path1)
df2 = pd.read_csv(file_path2, sep=';')


# Limpeza dos dados
df1 = clean_column(df1, 'LONGITUDE')
df1 = clean_column(df1, 'LATITUDE')
df2 = clean_column(df2, 'QT_VOTOS')

# Renomear colunas em df1
df1.rename(columns={
    'LONGITUDE': 'Longitude',
    'LATITUDE': 'Latitude',
    'QT_ELEITOR': 'Quantidade_Eleitores'
}, inplace=True)

# Agrupar votos por local de votação em df2
df2_grouped = df2.groupby('NR_LOCAL_VOTACAO', as_index=False).agg({
    'QT_VOTOS': 'sum'
})

# Unir df1 com df2_grouped
df1 = df1.merge(df2_grouped, left_on='NR_LOCAL_V',
                right_on='NR_LOCAL_VOTACAO', how='left')



# Agrupar por localização e somar os eleitores
df1_grouped = df1.groupby(['Longitude', 'Latitude', 'NM_LOCAL_V', 'NR_LOCAL_V', 'DS_TIPO_LO'], as_index=False).agg({
    'Quantidade_Eleitores': 'sum',
    'QT_VOTOS': 'mean'
})

# Sidebar para seleção de local
st.sidebar.header("Selecione um Local de Votação")

# Adicionar uma opção para "Todos os Locais"
local_options = ['Todos os Locais'] + \
    df1_grouped['NM_LOCAL_V'].unique().tolist()

selected_local = st.sidebar.selectbox(
    "Escolha o Local de Votação",
    options=local_options
)

# Filtrar dados com base na seleção
if selected_local == 'Todos os Locais':
    filtered_df = df1_grouped
else:
    filtered_df = df1_grouped[df1_grouped['NM_LOCAL_V'] == selected_local]

st.write('Dados:')
st.write(filtered_df)

# Criação do mapa com folium
st.title("Mapa de Locais de Votação")

# Inicializa o mapa em uma localização central
m = folium.Map(location=[filtered_df['Latitude'].mean(),
               filtered_df['Longitude'].mean()], zoom_start=11)

# Adiciona um cluster de marcadores ao mapa
marker_cluster = MarkerCluster().add_to(m)

# Adiciona marcadores para o local selecionado
for idx, row in filtered_df.iterrows():
    popup_content = f"""
    <strong>Número:</strong> {row['NR_LOCAL_V']}<br>
    <strong>Local:</strong> {row['NM_LOCAL_V']}<br>
    <strong>Tipo:</strong> {row['DS_TIPO_LO']}<br>
    <strong>Total Eleitores:</strong> {row['Quantidade_Eleitores']}<br>
    <strong>Total Votos:</strong> {row['QT_VOTOS']}
    """
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=folium.Popup(popup_content, max_width=300),
        icon=folium.Icon(color='blue')
    ).add_to(marker_cluster)

st_data = st_folium(m, use_container_width=True)

# Detecção de clique no mapa
clicked_object = st_data.get('last_object_clicked_popup', None)
st.title("Detalhes:")
if clicked_object:
    st.write(clicked_object)
    # Buscar o número do local de votação a partir do objeto clicado
    print('clicked_object', clicked_object)
    match = re.search(r'Número: (\d+)', clicked_object)
    print('match: ', match)
    if match:
        nr_local_v = int(match.group(1))
        print(f'O número do local de votação é: {nr_local_v}')
        # Filtrar o DataFrame df2 para o local de votação desejado

        df_vereadores = df2[df2['NR_LOCAL_VOTACAO'] == nr_local_v]

        # Agrupar por vereador e somar os votos
        df_vereadores_grouped = df_vereadores.groupby(['NM_VOTAVEL'], as_index=False).agg({
            'QT_VOTOS': 'sum'
        })

        # Ordenar por quantidade de votos, se desejado
        df_vereadores_grouped = df_vereadores_grouped.sort_values(
            by='QT_VOTOS', ascending=False)

        # Mostrar os dados
        st.write('Balanço dos Votos dos Vereadores:')
        st.dataframe(df_vereadores_grouped, use_container_width=True)

    else:
        print('Número do local de votação não encontrado.')

else:
    st.write('Selecione um Local para mais detalhes.')
