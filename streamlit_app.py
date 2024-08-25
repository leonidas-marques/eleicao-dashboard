import streamlit as st
import pandas as pd
import pydeck as pdk

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

# Criação do mapa com pydeck
st.title("Mapa de Locais de Votação")

# Configurações do mapa
map_layers = [
    pdk.Layer(
        "ColumnLayer",
        data=df1_grouped,
        get_position=["Longitude", "Latitude"],
        # Altura da coluna baseada na quantidade de votos
        get_elevation="QT_VOTOS",
        elevation_scale=0.1,
        get_color=[0, 128, 255, 200],  # Cor das colunas de votos
        radius=50,
        pickable=True,
        extruded=True,
    )
]

view_state = pdk.ViewState(
    latitude=df1['Latitude'].mean(),
    longitude=df1['Longitude'].mean(),
    zoom=11,
    pitch=50,  # Ajuste o ângulo para melhor visualização
)

# Exibir o mapa no Streamlit
deck = pdk.Deck(
    layers=map_layers,
    initial_view_state=view_state,
    tooltip={
        "text": "Local: {NM_LOCAL_V}\nTipo: {DS_TIPO_LO}\n Total Eleitores: {Quantidade_Eleitores} \nTotal Votos: {QT_VOTOS}"
    }
)
st.pydeck_chart(deck)
