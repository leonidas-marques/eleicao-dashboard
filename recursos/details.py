import re
import streamlit as st


def load_details(clicked_object, df2):

    if clicked_object:
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
