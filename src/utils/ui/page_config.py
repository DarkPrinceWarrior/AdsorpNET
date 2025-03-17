"""
Модуль для конфигурации страниц Streamlit.
"""

import streamlit as st

def load_theme_css():
    """
    Загружает стили темы без вызова set_page_config.
    Используется для сохранения темы в страницах.
    """
    # Загружаем пользовательские стили
    css = """
    <style>
        /* Light theme */
        [data-theme="light"] {
            --background-color: #ffffff;
            --text-color: #000000;
            --primary-color: #ff4b4b;
        }
        
        /* Dark theme */
        [data-theme="dark"] {
            --background-color: #0e1117;
            --text-color: #ffffff;
            --primary-color: #ff4b4b;
        }
        
        /* Common styles */
        .stButton>button {
            border-radius: 20px;
            padding: 10px 24px;
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .stProgress > div > div {
            background-color: var(--primary-color);
        }
        
        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .st-emotion-cache-1v0mbdj {
            animation: fadeIn 0.5s ease-in;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def load_user_preferences():
    """Загружает пользовательские настройки."""
    # Здесь можно добавить загрузку пользовательских настроек из файла или базы данных
    if "theme" not in st.session_state:
        st.session_state.theme = "light"