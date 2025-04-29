"""
Модуль для конфигурации страниц Streamlit.
"""

import streamlit as st

def load_theme_css() -> None:
    css = """
    <style>
    /* ---------- SIDEBAR ---------- */
    section[data-testid="stSidebar"]{
        background: linear-gradient(180deg,#0B2545 0%,#193B73 100%);
        color:#F2F6FA;
        padding-top:2rem;
        box-shadow:4px 0 12px rgba(0,0,0,.15);
    }
    /* заголовки внутри меню */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3{
        color:#F2F6FA;
        font-weight:600;
        letter-spacing:.3px;
    }
    /* все интерактивные контролы */
    section[data-testid="stSidebar"] .stButton>button,
    section[data-testid="stSidebar"] [data-baseweb="input"] input,
    section[data-testid="stSidebar"] [data-baseweb="select"] div{
        background:rgba(255,255,255,.08);
        border:none;
        border-radius:8px;
        color:#F2F6FA;
        transition:background .3s;
    }
    section[data-testid="stSidebar"] .stButton>button:hover,
    section[data-testid="stSidebar"] [data-baseweb="select"]:hover div{
        background:rgba(255,255,255,.15);
    }
    /* радиокнопки / чекбоксы */
    section[data-testid="stSidebar"] input[type="radio"],
    section[data-testid="stSidebar"] input[type="checkbox"]{
        accent-color:#FFB703;
    }
    /* скролл-бар для длинного меню */
    section[data-testid="stSidebar"]::-webkit-scrollbar{
        width:6px;
    }
    section[data-testid="stSidebar"]::-webkit-scrollbar-thumb{
        background:#FFB703;
        border-radius:3px;
    }
    </style>
    """
    import streamlit as st
    st.markdown(css, unsafe_allow_html=True)

def load_user_preferences():
    """Загружает пользовательские настройки."""
    # Здесь можно добавить загрузку пользовательских настроек из файла или базы данных
    if "theme" not in st.session_state:
        st.session_state.theme = "light"