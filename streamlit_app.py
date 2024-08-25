from streamlit_folium import folium_static  # Importação correta
import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster

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
    'QT_VOTOS': 'sum'
})

st.write('Agrupar por localização e somar os eleitores')
st.write(df1_grouped)

# Criação do mapa com folium
st.title("Mapa de Locais de Votação")

# Inicializa o mapa em uma localização central
m = folium.Map(location=[df1['Latitude'].mean(),
               df1['Longitude'].mean()], zoom_start=11)

# Adiciona um cluster de marcadores ao mapa
marker_cluster = MarkerCluster().add_to(m)

# Adiciona marcadores para cada local de votação
for idx, row in df1_grouped.iterrows():
    popup_content = f"""
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

# Exibir o mapa no Streamlit
folium_static(m)
