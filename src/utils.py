import streamlit as st
from pathlib import Path
import json

def set_page_config():
    """Устанавливает базовую конфигурацию страницы"""
    st.set_page_config(
        page_title="AdsorpNET",
        page_icon="🧪",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    # Загружаем пользовательские стили
    load_custom_css()
    
    # Устанавливаем тему
    if "theme" not in st.session_state:
        st.session_state.theme = "light"
    
    # Добавляем переключатель темы в сайдбар
    with st.sidebar:
        theme = st.radio(
            "Тема оформления",
            ("light", "dark"),
            key="theme",
            on_change=switch_theme
        )

def load_custom_css():
    """Загружает пользовательские стили CSS"""
    custom_css = """
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
    st.markdown(custom_css, unsafe_allow_html=True)

def switch_theme():
    """Переключает тему оформления"""
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
    
def save_user_preferences():
    """Сохраняет пользовательские настройки"""
    prefs_path = Path("user_preferences.json")
    preferences = {
        "theme": st.session_state.theme,
    }
    with open(prefs_path, "w") as f:
        json.dump(preferences, f)
        
def load_user_preferences():
    """Загружает пользовательские настройки"""
    prefs_path = Path("user_preferences.json")
    if prefs_path.exists():
        with open(prefs_path) as f:
            preferences = json.load(f)
            st.session_state.update(preferences)

def show_error_message(message: str):
    """Показывает сообщение об ошибке"""
    st.error(f"❌ {message}")
    
def show_success_message(message: str):
    """Показывает сообщение об успехе"""
    st.success(f"✅ {message}")
    
def show_info_message(message: str):
    """Показывает информационное сообщение"""
    st.info(f"ℹ️ {message}")
    
def show_warning_message(message: str):
    """Показывает предупреждение"""
    st.warning(f"⚠️ {message}")

def rate_limit(key: str, max_calls: int, time_window: int = 60):
    """
    Простой rate limiter для ограничения частоты вызовов
    
    Args:
        key (str): Уникальный ключ для идентификации вызова
        max_calls (int): Максимальное количество вызовов
        time_window (int): Временное окно в секундах
    
    Returns:
        bool: True если вызов разрешен, False если превышен лимит
    """
    import time
    
    if "rate_limit" not in st.session_state:
        st.session_state.rate_limit = {}
    
    current_time = time.time()
    rate_limit_key = f"rate_limit_{key}"
    
    if rate_limit_key not in st.session_state.rate_limit:
        st.session_state.rate_limit[rate_limit_key] = []
    
    # Очищаем старые записи
    st.session_state.rate_limit[rate_limit_key] = [
        t for t in st.session_state.rate_limit[rate_limit_key]
        if current_time - t < time_window
    ]
    
    # Проверяем лимит
    if len(st.session_state.rate_limit[rate_limit_key]) >= max_calls:
        return False
    
    # Добавляем новый вызов
    st.session_state.rate_limit[rate_limit_key].append(current_time)
    return True 