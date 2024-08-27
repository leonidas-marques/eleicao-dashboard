import re
import streamlit as st
import plotly.express as px


def load_vereadores(selected_vereador, df1_grouped):
    if selected_vereador != 'Todos os Vereadores':

        df_vereador_bairro = df1_grouped.groupby('NM_BAIRRO').agg({
            selected_vereador: 'sum'
        }).reset_index()

        df_vereador_bairro.rename(
            columns={selected_vereador: 'Votos'}, inplace=True)

        # Filtrar bairros com votos > 0
        df_vereador_bairro = df_vereador_bairro[df_vereador_bairro['Votos'] > 0]

        df_vereador_bairro = df_vereador_bairro.sort_values(
            by='Votos', ascending=True)

        fig = px.pie(df_vereador_bairro, names='NM_BAIRRO', values='Votos',
                     title=f'Quantidade de Votos por Bairro para {selected_vereador}',
                     labels={'NM_BAIRRO': 'Bairro', 'Votos': 'Quantidade de Votos'})
        fig.update_traces(textinfo='value')

        st.plotly_chart(fig, use_container_width=True)
