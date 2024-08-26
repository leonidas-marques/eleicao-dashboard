import re
import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import plotly.express as px


def clean_column(df, column_name):
    df[column_name] = df[column_name].astype(str)
    df[column_name] = df[column_name].str.replace(r'[()]*', '', regex=True)
    df[column_name] = df[column_name].str.replace(',', '.', regex=False)
    df[column_name] = pd.to_numeric(df[column_name], errors='coerce')
    return df


file_path1 = "./data/eleitorado_local_votacao_2020_geografica.xlsx"
file_path2 = "./data/votação_secão_2020 vereador.csv"

df1 = pd.read_excel(file_path1)
df2 = pd.read_csv(file_path2, sep=';')

df1 = clean_column(df1, 'LONGITUDE')
df1 = clean_column(df1, 'LATITUDE')
df2 = clean_column(df2, 'QT_VOTOS')

df1.rename(columns={
    'LONGITUDE': 'Longitude',
    'LATITUDE': 'Latitude',
    'QT_ELEITOR': 'Quantidade_Eleitores'
}, inplace=True)

df2_grouped = df2.groupby('NR_LOCAL_VOTACAO', as_index=False).agg({
    'QT_VOTOS': 'sum'
})

df1 = df1.merge(df2_grouped, left_on='NR_LOCAL_V',
                right_on='NR_LOCAL_VOTACAO', how='left')

df2_pivot = df2.pivot_table(index='NR_LOCAL_VOTACAO', columns='NM_VOTAVEL',
                            values='QT_VOTOS', aggfunc='sum', fill_value=0)

df1 = df1.merge(df2_pivot, left_on='NR_LOCAL_V',
                right_on='NR_LOCAL_VOTACAO', how='left')

df1_grouped = df1.groupby(['Longitude', 'Latitude', 'NM_BAIRRO', 'NM_LOCAL_V', 'NR_LOCAL_V', 'DS_TIPO_LO'], as_index=False).agg({
    'Quantidade_Eleitores': 'sum',
    'QT_VOTOS': 'mean',
    **{col: 'mean' for col in df2_pivot.columns}
})

st.sidebar.header("Selecione um Local de Votação")

vereador_options = ['Todos os Vereadores'] + \
    df2['NM_VOTAVEL'].unique().tolist()

local_options = ['Todos os Locais'] + \
    df1_grouped['NM_LOCAL_V'].unique().tolist()

bairro_options = ['Todos os Bairros'] + \
    df1_grouped['NM_BAIRRO'].unique().tolist()

selected_vereador = st.sidebar.selectbox(
    "Escolha o Vereador",
    options=vereador_options
)

selected_local = st.sidebar.selectbox(
    "Escolha o Local de Votação",
    options=local_options
)
selected_bairro = st.sidebar.selectbox(
    "Escolha o Bairro da Votação",
    options=bairro_options
)

if selected_local == 'Todos os Locais' and selected_bairro == 'Todos os Bairros':
    filtered_df = df1_grouped
elif selected_local == 'Todos os Locais':
    filtered_df = df1_grouped[df1_grouped['NM_BAIRRO'] == selected_bairro]
elif selected_bairro == 'Todos os Bairros':
    filtered_df = df1_grouped[df1_grouped['NM_LOCAL_V'] == selected_local]
else:
    filtered_df = df1_grouped[
        (df1_grouped['NM_LOCAL_V'] == selected_local) &
        (df1_grouped['NM_BAIRRO'] == selected_bairro)
    ]

st.title("Mapa de Locais de Votação")

m = folium.Map(location=[filtered_df['Latitude'].mean(),
               filtered_df['Longitude'].mean()], zoom_start=11)

marker_cluster = MarkerCluster().add_to(m)


def safe_int_conversion(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0


for idx, row in filtered_df.iterrows():
    if (selected_vereador != 'Todos os Vereadores'):
        popup_content = f"""
        <strong>Seção:</strong> {row['NR_LOCAL_V']}<br>
        <strong>Local:</strong> {row['NM_LOCAL_V']}<br>
        <strong>{selected_vereador} Votos:</strong> {safe_int_conversion(row[f'{selected_vereador}'])}<br>
        """
    else:
        popup_content = f"""
        <strong>Seção:</strong> {row['NR_LOCAL_V']}<br>
        <strong>Local:</strong> {row['NM_LOCAL_V']}<br>
        <strong>Total Eleitores:</strong> {row['Quantidade_Eleitores']}<br>
        <strong>Total Votos:</strong>{safe_int_conversion(row['QT_VOTOS'])}
        """
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=folium.Popup(popup_content, max_width=300),
        icon=folium.Icon(color='blue')
    ).add_to(marker_cluster)

st_data = st_folium(m, use_container_width=True)

clicked_object = st_data.get('last_object_clicked_popup', None)
st.title("Detalhes:")
if clicked_object:
    st.write(clicked_object)
    match = re.search(r'Seção: (\d+)', clicked_object)
    if match:
        nr_local_v = int(match.group(1))
        df_vereadores = df2[df2['NR_LOCAL_VOTACAO'] == nr_local_v]

        df_vereadores_grouped = df_vereadores.groupby(['NM_VOTAVEL', 'NR_VOTAVEL'], as_index=False).agg({
            'QT_VOTOS': 'sum'
        })

        df_vereadores_grouped = df_vereadores_grouped.sort_values(
            by='QT_VOTOS', ascending=False)

        df_vereadores_grouped.rename(columns={
            'NR_VOTAVEL': 'Número do vereador',
            'NM_VOTAVEL': 'Nome do vereador',
            'QT_VOTOS': 'Quantidade de votos'
        }, inplace=True)

        df_vereadores_grouped['Número do vereador'] = df_vereadores_grouped['Número do vereador'].astype(
            str)

        st.write('Balanço dos Votos dos Vereadores:')
        st.dataframe(df_vereadores_grouped,
                     use_container_width=True, hide_index=True)

    else:
        st.write('Número do local de votação não encontrado.')

else:
    st.write('Selecione um Local para mais detalhes.')

if selected_vereador != 'Todos os Vereadores':
    df_vereador_bairro = df1_grouped.groupby('NM_BAIRRO').agg({
        selected_vereador: 'sum'
    }).reset_index()

    df_vereador_bairro.rename(
        columns={selected_vereador: 'Votos'}, inplace=True)

    df_vereador_bairro = df_vereador_bairro.sort_values(
        by='Votos', ascending=False)

    fig = px.bar(df_vereador_bairro, y='NM_BAIRRO', x='Votos', title=f'Quantidade de Votos por Bairro para {selected_vereador}',
                 labels={'NM_BAIRRO': 'Bairro', 'Votos': 'Quantidade de Votos'})

    st.plotly_chart(fig, use_container_width=True)
