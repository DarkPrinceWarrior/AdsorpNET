"""
Главный файл приложения AdsorpNET.
"""

import streamlit as st
from streamlit_option_menu import option_menu
import logging
from pathlib import Path

# Настраиваем базовую конфигурацию - ДОЛЖНО БЫТЬ ПЕРВОЙ КОМАНДОЙ STREAMLIT!
st.set_page_config(
    page_title="AdsorpNET - AI сервис пористых материалов",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

def add_custom_styles():
    """Добавляет кастомные стили для профессиональной навигационной панели с цветами проекта."""
    
    st.markdown('<link rel="stylesheet" href="static/accessibility.css">', unsafe_allow_html=True)
    st.markdown("""
    <style>
    /* Глобальные цвета темы - в соответствии с проектом */
    :root {
        --primary-color: #FF4B4B; /* Красный акцент */
        --secondary-color: #0B2545; /* Темно-синий фон */
        --accent-color: #134074; /* Средний синий */
        --highlight-color: #8DA9C4; /* Светло-синий */
        --text-color: #FFFFFF; /* Белый текст */
    }
    
    /* Усовершенствованный стиль для сайдбара */
    section.st-emotion-cache-vk3wp9.e1fqkh3o11, 
    section[data-testid="stSidebar"],
    div.st-emotion-cache-6qob1r.e1fqkh3o3 {
        background: linear-gradient(150deg, #0b2545 0%, #173b73 90%);
        width: auto !important;
        min-width: 250px !important;
        max-width: 320px !important;
        box-shadow: 2px 0 16px rgba(0,0,0,0.3) !important;
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Стилизация изображения логотипа */
    .st-emotion-cache-1kyxreq.e1tzin5v3 img {
        margin: 0 auto;
        display: block;
        max-width: 90%;
        height: auto;
        transition: transform 0.3s ease;
    }
    
    .st-emotion-cache-1kyxreq.e1tzin5v3 img:hover {
        transform: scale(1.02);
    }
    
    /* Улучшенные стили для навигационных пунктов */
    .nav-link {
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        font-size: 16px !important;
        margin: 4px 0 !important;
        border-radius: 6px !important;
        transition: all 0.3s ease !important;
    }
    
    .nav-link:hover {
        background-color: rgba(255,255,255,0.1) !important;
        color: #ffffff !important;
        transform: translateX(3px);
        letter-spacing: 0.3px;
    }
    
    /* Анимации и эффекты для выбранного элемента */
    .nav-link-selected {
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
    }
    
    /* Настройка адаптивности сайдбара */
    @media (min-width: 1200px) {
        section[data-testid="stSidebar"] {
            min-width: 280px !important;
            max-width: 320px !important;
        }
    }
    
    @media (max-width: 1199px) and (min-width: 992px) {
        section[data-testid="stSidebar"] {
            min-width: 260px !important;
            max-width: 300px !important;
        }
    }
    
    @media (max-width: 991px) and (min-width: 768px) {
        section[data-testid="stSidebar"] {
            min-width: 240px !important;
            max-width: 280px !important;
        }
    }
    
    @media (max-width: 767px) {
        section[data-testid="stSidebar"] {
            min-width: 220px !important;
            max-width: 260px !important;
        }
    }
    
    /* Убираем лишние отступы и рамки */
    .css-1544g2n.e1fqkh3o4 {
        padding: 0 !important;
    }
    
    /* Улучшенные стили для скролл-бара */
    ::-webkit-scrollbar {
        width: 5px;
        height: 5px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(0,0,0,0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(45deg, #FF4B4B, #ff6b6b);
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #ff3b3b;
    }
    
    /* Фикс для отображения контента */
    .stApp {
        overflow-x: hidden;
    }
    
    /* Исправление для горизонтального скролла */
    .st-emotion-cache-18ni7ap.ezrtsby2 {
        overflow-x: auto !important;
    }
    
    /* Убираем отступы в контейнерах */
    div.st-emotion-cache-16txtl3.eczjsme4 {
        padding: 0 !important;
    }
    
    /* Стили для всех селекторов меню */
    div[data-testid="stVerticalBlock"] div[data-baseweb="select"] div,
    div[data-testid="stVerticalBlock"] div[role="listbox"],
    div[data-testid="stVerticalBlock"] div[data-baseweb="select"] ul {
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    
    /* Улучшенные стили для streamlit-option-menu */
    #MainMenu, #main-menu, #main_menu {
        white-space: nowrap !important;
        overflow: hidden !important;
        font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }
    
    /* Корректировка отступов в меню */
    .css-17ziqus, .css-pkbazv, .st-emotion-cache-17ziqus, .st-emotion-cache-pkbazv {
        padding-left: 15px !important;
        padding-right: 15px !important;
    }
    
    /* Установка фиксированной ширины основных элементов меню */
    .css-17ziqus, .st-emotion-cache-17ziqus {
        width: 100% !important;
        max-width: 300px !important;
    }
    
    /* Уменьшаем размер значков в меню и добавляем анимацию */
    .nav-link svg {
        width: 18px !important;
        height: 18px !important;
        margin-right: 10px !important;
        transition: transform 0.3s ease !important;
    }
    
    .nav-link:hover svg {
        transform: translateX(2px) !important;
    }
    
    /* Делаем текст меню более заметным */
    .nav-link span {
        font-weight: 500 !important;
        letter-spacing: 0.5px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Импорты из структурированных модулей
from src.pages import home, analysis, predict, team, info
from src.utils.ui import load_user_preferences
from src.utils.storage import clear_prediction_cache
from src.services.model_service import ModelService
from src.config.app_config import LOGGING_CONFIG
from src.config.model_config import MODEL_CONFIG

# Настройка логирования
import logging.config
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

# Загружаем стили
def load_styles():
    """Загружает CSS стили для приложения."""
    css_path = Path("static/style.css")
    if css_path.exists():
        with open(css_path, encoding='utf-8') as css_file:
            st.markdown(f'<style>{css_file.read()}</style>', unsafe_allow_html=True)
    else:
        logger.error(f"Файл стилей не найден: {css_path}")

def initialize_services():
    """Инициализирует сервисы приложения."""
    # Инициализируем сервис моделей (ленивая загрузка)
    if 'model_service' not in st.session_state:
        logger.info("Инициализация сервиса моделей")
        st.session_state.model_service = ModelService()
        
    # Проверяем кэш предсказаний
    if 'cache_cleared' not in st.session_state:
        st.session_state.cache_cleared = False
    
    # Очищаем кэш при запуске приложения (только один раз)
    if not st.session_state.cache_cleared:
        clear_prediction_cache()
        st.session_state.cache_cleared = True
        logger.info("Кэш предсказаний очищен при инициализации")

def create_sidebar():
    """Создает профессиональную навигационную панель с цветами проекта."""
    
    # Создаем адаптивный контейнер для сайдбара
    with st.sidebar:
        # Контейнер для логотипа с отступами и улучшенным отображением
        with st.container():
            st.image("images/logo.png", use_container_width=True)
        
        # Элегантный разделитель после логотипа
        st.markdown("""
        <div style="height:2px; background: linear-gradient(90deg, rgba(255,255,255,0), rgba(255,75,75,0.5), rgba(255,255,255,0)); 
        margin: 15px 0 20px 0; border-radius: 2px;"></div>
        """, unsafe_allow_html=True)
        
        # Добавляем красивое меню с помощью streamlit-option-menu
        # с улучшенными стилями и анимацией
        selected = option_menu(
            menu_title=None,
            options=[
                "Главная", 
                "О MOF", 
                "AI синтез", 
                "Анализ", 
                "О проекте"
            ],
            icons=[
                "house-fill", 
                "info-circle-fill", 
                "cpu-fill", 
                "graph-up", 
                "people-fill"
            ],
            default_index=0,
            key="main_menu",
            styles={
                "container": {
                    "padding": "0px", 
                    "background-color": "#0B2545",
                    "max-width": "100%",
                    "border-radius": "8px",
                    "overflow": "hidden",
                    "box-shadow": "0 4px 6px rgba(0,0,0,0.1)"
                },
                "icon": {
                    "color": "#FF4B4B",
                    "font-size": "16px",
                    "transition": "all 0.3s ease"
                },
                "nav-link": {
                    "font-size": "16px", 
                    "text-align": "left", 
                    "margin": "0px", 
                    "padding": "12px 15px",
                    "border-radius": "0px",
                    "--hover-color": "#13315C",
                    "white-space": "nowrap",
                    "overflow": "hidden",
                    "text-overflow": "ellipsis",
                    "display": "flex",
                    "align-items": "center",
                    "color": "#FFFFFF",
                    "font-weight": "500",
                    "transition": "all 0.3s ease"
                },
                "nav-link-selected": {
                    "background-color": "#13315C",
                    "font-weight": "bold",
                    "color": "#FF4B4B",
                    "border-left": "3px solid #FF4B4B",
                    "transform": "translateX(2px)"
                }
            }
        )
        
        # Добавляем элегантный футер в нижней части сайдбара
        st.markdown("""
        <div style="position: fixed; bottom: 0; left: 0; width: 100%; background: linear-gradient(0deg, #0B2545 0%, transparent 100%); 
        padding: 15px 15px 10px 15px; text-align: center; font-size: 12px; color: rgba(255,255,255,0.7);">
            AdsorpNET © 2025<br>
            ИФХЭ РАН
        </div>
        """, unsafe_allow_html=True)
        
        return selected

def run():
    """Запускает приложение AdsorpNET."""
    try:
        # Логируем запуск приложения
        logger.info("Запуск приложения AdsorpNET")
        
        # Загружаем пользовательские настройки
        load_user_preferences()
        
        # Загружаем стили
        load_styles()
        
        # Добавляем кастомные стили для навигационной панели
        add_custom_styles()
        
        # Инициализируем сервисы
        initialize_services()
        
        # Создаем боковое меню и получаем выбранный пункт
        selected = create_sidebar()
        
        # Выбор и отображение страницы
        if selected == "Главная":
            home.show()
        elif selected == "AI синтез": # Сокращенное название
            predict.show()
        elif selected == "О MOF": # Сокращенное название
            info.show()
        elif selected == "Анализ":
            analysis.show()
        elif selected == "О проекте":
            team.show()
            
    except Exception as e:
        logger.error(f"Ошибка при запуске приложения: {str(e)}", exc_info=True)
        st.error(f"Произошла ошибка при запуске приложения: {str(e)}")

if __name__ == "__main__":
    run()