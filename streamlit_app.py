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

# Função para gerenciar o valor de pitch


def manage_pitch():
    if 'pitch' not in st.session_state:
        st.session_state.pitch = 45  # Valor inicial do pitch

    col1, col2, col3 = st.sidebar.columns([1, 3, 1])

    with col1:
        if st.button('−', key='decrement_pitch'):
            st.session_state.pitch = max(0, st.session_state.pitch - 1)

    with col2:
        st.session_state.pitch = st.slider(
            "Inclinação (Pitch)", min_value=0, max_value=90, value=st.session_state.pitch)

    with col3:
        if st.button('＋', key='increment_pitch'):
            st.session_state.pitch = min(90, st.session_state.pitch + 1)

# Função para gerenciar o valor de zoom


def manage_zoom():
    if 'zoom' not in st.session_state:
        st.session_state.zoom = 12  # Valor inicial do zoom

    col1, col2, col3 = st.sidebar.columns([1, 3, 1])

    with col1:
        if st.button('−', key='decrement_zoom'):
            st.session_state.zoom = max(1, st.session_state.zoom - 1)

    with col2:
        st.session_state.zoom = st.slider(
            "Nível de Zoom", min_value=1, max_value=20, value=st.session_state.zoom)

    with col3:
        if st.button('＋', key='increment_zoom'):
            st.session_state.zoom = min(20, st.session_state.zoom + 1)


# Sidebar para upload do arquivo Excel e configurações do mapa
st.sidebar.header("Configurações do Mapa")
uploaded_file = st.sidebar.file_uploader(
    "Escolha um arquivo Excel", type=["xls", "xlsx"])

st.sidebar.markdown("<hr>", unsafe_allow_html=True)

# Barra de pesquisa para o campo "Local"
if uploaded_file is not None:
    try:
        manage_pitch()
        manage_zoom()
        color = st.sidebar.color_picker("Cor dos Marcadores", "#0000FF")
        df = pd.read_excel(uploaded_file)

        # st.write("Dados Importados:", df)

        required_columns = ["LONGITUDE", "LATITUDE",
                            "NM_LOCAL_V", "NM_BAIRRO", "QT_ELEITOR"]
        if all(col in df.columns for col in required_columns):
            df.rename(columns={
                "LONGITUDE": "Longitude",
                "LATITUDE": "Latitude",
                "NM_LOCAL_V": "Local",
                "NM_BAIRRO": "Bairro",
                "QT_ELEITOR": "Eleitores"
            }, inplace=True)

            df = clean_column(df, 'Longitude')
            df = clean_column(df, 'Latitude')

            unique_locations = df['Local'].dropna().unique()
            selected_local = st.sidebar.selectbox("Selecionar Local", options=[
                                                  ""] + list(unique_locations))

            if selected_local:
                df = df[df['Local'] == selected_local]

            df.dropna(subset=['Longitude', 'Latitude'], inplace=True)

            if not df.empty:
                # Criar a camada 3D
                layer = pdk.Layer(
                    "ColumnLayer",
                    data=df,
                    get_position=["Longitude", "Latitude"],
                    get_elevation="Eleitores",
                    radius=10,
                    elevation_scale=1,
                    get_fill_color=[
                        int(color[1:3], 16),
                        int(color[3:5], 16),
                        int(color[5:7], 16),
                        180
                    ],
                    pickable=True,
                    auto_highlight=True,
                    opacity=0.8
                )

                view_state = pdk.ViewState(
                    latitude=df['Latitude'].mean(),
                    longitude=df['Longitude'].mean(),
                    zoom=st.session_state.zoom,
                    pitch=st.session_state.pitch
                )

                deck_map = pdk.Deck(
                    layers=[layer],
                    initial_view_state=view_state,
                    tooltip={
                        "html": "<b>Local:</b> {Local}<br><b>Bairro:</b> {Bairro}<br><b>Eleitores:</b> {Eleitores}",
                        "style": {"color": "white"}
                    }
                )

                st.pydeck_chart(deck_map)

                # Adicionar gráfico de barras de votos por bairro
                bairro_counts = df.groupby(
                    'Bairro')['Eleitores'].sum().reset_index()
                st.write("Quantidade de Votos por Bairro:")
                st.bar_chart(bairro_counts.set_index('Bairro'))
            else:
                st.write("Nenhum dado encontrado para o local selecionado.")
        else:
            st.error("O arquivo Excel não contém todas as colunas necessárias.")
    except Exception as e:
        st.error(f"Ocorreu um erro ao processar o arquivo: {e}")
else:
    st.info("Faça o upload de um arquivo Excel para começar.")
