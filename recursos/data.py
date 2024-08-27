import pandas as pd
import streamlit as st


def clean_column(df, column_name):
    df[column_name] = df[column_name].astype(str)
    df[column_name] = df[column_name].str.replace(r'[()]*', '', regex=True)
    df[column_name] = df[column_name].str.replace(',', '.', regex=False)
    df[column_name] = pd.to_numeric(df[column_name], errors='coerce')
    return df


@st.cache_data
def load_data():

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

    return df1_grouped, df2
