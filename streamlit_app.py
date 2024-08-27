import streamlit as st

from recursos.data import load_data

from recursos.filters import load_filters

from recursos.layout import render_layout


import hmac
import streamlit as st

st.set_page_config(layout="wide")


def check_password():
    """Retorna `True` se o usuário tiver inserido a senha correta."""

    def login_form():
        """Formulário com widgets para coletar informações do usuário"""
        with st.form("Credentials"):
            st.text_input("Nome de usuário", key="username")
            st.text_input("Senha", type="password", key="password")
            st.form_submit_button("Entrar", on_click=password_entered)

    def password_entered():
        """Verifica se a senha inserida pelo usuário está correta."""
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            # Não armazene o nome de usuário ou senha.
            del st.session_state["password"]
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # Retorna True se o nome de usuário + senha forem validados.
    if st.session_state.get("password_correct", False):
        return True

    # Mostra os campos para nome de usuário + senha.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 Usuário desconhecido ou senha incorreta")
    return False


if not check_password():
    st.stop()


with st.spinner('Carregando dados...'):
    df1_grouped, df2 = load_data()
    filtered_df, selected_vereador = load_filters(df1_grouped, df2)
    render_layout(df2, filtered_df, selected_vereador, df1_grouped)
