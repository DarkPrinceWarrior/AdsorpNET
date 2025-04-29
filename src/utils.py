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

    # Устанавливаем тему (light по умолчанию)
    if "theme" not in st.session_state:
        st.session_state.theme = "light"

    # Добавляем переключатель темы в сайдбар
    with st.sidebar:
        st.radio(
            "Тема оформления",
            ("light", "dark"),
            key="theme",
            on_change=switch_theme,
            horizontal=True,
        )


def load_custom_css() -> None:
    """Подключает глобальные и сайдбар‑специфичные стили CSS"""

    # === Глобальные переменные и анимации ===
    base_css = """
    <style>
    /* ---------- THEME TOKENS ---------- */
    [data-theme="light"] {
        --background-color: #ffffff;
        --text-color: #000000;
        --primary-color: #ff4b4b;
        --sidebar-bg: linear-gradient(180deg,#ffffff 0%,#f5f7fa 100%);
        --sidebar-fg: #0B2545;
    }
    [data-theme="dark"] {
        --background-color: #0e1117;
        --text-color: #ffffff;
        --primary-color: #ff4b4b;
        --sidebar-bg: linear-gradient(180deg,#0B2545 0%,#193B73 100%);
        --sidebar-fg: #F2F6FA;
    }

    /* ---------- GLOBAL CONTROLS ---------- */
    .stButton>button {
        border-radius: 20px;
        padding: 10px 24px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .stProgress>div>div {
        background-color: var(--primary-color);
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to   { opacity: 1; }
    }
    .st-emotion-cache-1v0mbdj { animation: fadeIn .5s ease-in; }

    /* ---------- SIDEBAR ---------- */
    [data-theme] section[data-testid="stSidebar"] {
        background: var(--sidebar-bg);
        color: var(--sidebar-fg);
        padding-top: 2rem;
        box-shadow: 4px 0 12px rgba(0,0,0,.15);
    }
    [data-theme] section[data-testid="stSidebar"] h1,
    [data-theme] section[data-testid="stSidebar"] h2,
    [data-theme] section[data-testid="stSidebar"] h3 {
        color: var(--sidebar-fg);
        font-weight: 600;
        letter-spacing: .3px;
    }
    /* Интерактивные элементы внутри сайдбара */
    [data-theme] section[data-testid="stSidebar"] .stButton>button,
    [data-theme] section[data-testid="stSidebar"] div[data-baseweb="input"] input,
    [data-theme] section[data-testid="stSidebar"] div[data-baseweb="select"] div {
        background: rgba(255,255,255,.08);
        border: none;
        border-radius: 8px;
        color: var(--sidebar-fg);
        transition: background .3s;
    }
    [data-theme] section[data-testid="stSidebar"] .stButton>button:hover,
    [data-theme] section[data-testid="stSidebar"] div[data-baseweb="select"]:hover div {
        background: rgba(255,255,255,.15);
    }
    /* Радио‑ и чекбоксы */
    [data-theme] section[data-testid="stSidebar"] input[type="radio"],
    [data-theme] section[data-testid="stSidebar"] input[type="checkbox"] {
        accent-color: #FFB703;
    }
    /* Кастомный скроллбар */
    [data-theme] section[data-testid="stSidebar"]::-webkit-scrollbar { width: 6px; }
    [data-theme] section[data-testid="stSidebar"]::-webkit-scrollbar-thumb {
        background: #FFB703; border-radius: 3px;
    }
    </style>
    """

    st.markdown(base_css, unsafe_allow_html=True)


def switch_theme() -> None:
    """Переключает тему оформления."""
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"


# ----- USER PREFERENCES -------------------------------------------------- #

def save_user_preferences() -> None:
    """Сохраняет пользовательские настройки (сейчас: только тема)."""
    prefs_path = Path("user_preferences.json")
    with open(prefs_path, "w", encoding="utf-8") as f:
        json.dump({"theme": st.session_state.theme}, f)


def load_user_preferences() -> None:
    """Загружает сохранённые пользовательские настройки, если файл существует."""
    prefs_path = Path("user_preferences.json")
    if prefs_path.exists():
        with open(prefs_path, encoding="utf-8") as f:
            st.session_state.update(json.load(f))


# ----- MESSAGE HELPERS --------------------------------------------------- #

def show_error_message(message: str) -> None:
    st.error(f"❌ {message}")


def show_success_message(message: str) -> None:
    st.success(f"✅ {message}")


def show_info_message(message: str) -> None:
    st.info(f"ℹ️ {message}")


def show_warning_message(message: str) -> None:
    st.warning(f"⚠️ {message}")


# ----- SIMPLE RATE LIMIT ------------------------------------------------- #

def rate_limit(key: str, max_calls: int, time_window: int = 60) -> bool:
    """Ограничивает частоту вызовов функции в рамках *time_window* секунд."""
    import time

    if "rate_limit" not in st.session_state:
        st.session_state.rate_limit = {}

    current_time = time.time()
    rl_key = f"rate_limit_{key}"
    calls = st.session_state.rate_limit.setdefault(rl_key, [])

    # Удаляем устаревшие вызовы
    st.session_state.rate_limit[rl_key] = calls = [t for t in calls if current_time - t < time_window]

    if len(calls) >= max_calls:
        return False

    calls.append(current_time)
    return True
