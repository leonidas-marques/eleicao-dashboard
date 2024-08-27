import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium


def render_map(filtered_df, selected_vereador):
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

    return st_folium(m, use_container_width=True, height=450)
