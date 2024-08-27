import streamlit as st


def load_filters(df1_grouped, df2):

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

    return filtered_df, selected_vereador
