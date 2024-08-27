import streamlit as st


from recursos.details import load_details
from recursos.map import render_map
from recursos.vereadores import load_vereadores


def render_layout(df2, filtered_df, selected_vereador, df1_grouped):
    left_column, right_column = st.columns(2)

    with left_column:
        st_data = render_map(filtered_df, selected_vereador)
        clicked_object = st_data.get('last_object_clicked_popup', None)

    with right_column:
        load_details(clicked_object, df2)

    load_vereadores(selected_vereador, df1_grouped)
