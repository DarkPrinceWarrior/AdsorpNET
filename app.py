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
    """Добавляет кастомные стили для навигационной панели."""
    st.markdown("""
    <style>
    /* Глобальные цвета темы */
    :root {
        --primary-color: #4ECDC4;
        --secondary-color: #1E2D3A;
        --accent-color: #FF6B6B;
        --text-color: #FFFFFF;
        --background-color: #1A1A1A;
    }
    
    /* Стили для боковой панели */
    .css-1d391kg {
        background-color: var(--secondary-color);
    }
    
    /* Стиль для контейнера sidebar */
    .css-1cypcdb.e1fqkh3o11 {
        background-color: var(--secondary-color) !important;
    }
    
    /* Ховер эффекты для элементов меню */
    .nav-link:hover {
        background-color: #2B3E4F !important;
        transition: all 0.3s ease;
    }
    
    /* Анимация при выборе элемента */
    .nav-link-selected {
        transition: all 0.3s ease !important;
    }
    
    /* Стили для кнопок expander */
    .st-emotion-cache-rklbre h5 {
        color: var(--primary-color) !important;
        margin-bottom: 10px;
        font-size: 0.9rem !important;
    }
    
    /* Стили для футера */
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: var(--secondary-color);
        color: var(--text-color);
        text-align: center;
        padding: 10px;
        font-size: 0.8rem;
    }
    
    /* Скролл-бар */
    ::-webkit-scrollbar {
        width: 5px;
        height: 5px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--secondary-color);
    }
    
    ::-webkit-scrollbar-thumb {
        background: #4ECDC4;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #3DAAA2;
    }
    
    /* Стили для заголовка сайдбара */
    .st-emotion-cache-10oheav {
        padding-top: 1rem !important;
    }
    
    /* Стили для экспандера в сайдбаре */
    .st-emotion-cache-jy4u63 {
        background-color: #2B3E4F !important;
        border-radius: 5px !important;
        margin-bottom: 10px !important;
    }
    
    /* Удалить границу из сайдбара */
    .css-1cypcdb.e1fqkh3o11, .css-1r6o8ze.edgvbvh5 {
        border-right: none !important;
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
    """Создает профессиональную навигационную панель."""
    with st.sidebar:
        # Добавляем логотип
        st.image("images/logo.png", width=150, use_container_width=False)
        
        # Добавляем красивое меню с помощью streamlit-option-menu
        selected = option_menu(
            menu_title="AdsorpNET",
            options=[
                "Главная", 
                "О металлорганических каркасах", 
                "AI синтез MOF", 
                "Анализ структуры", 
                "О проекте"
            ],
            icons=[
                "house-fill", 
                "info-circle-fill", 
                "cpu-fill", 
                "graph-up", 
                "people-fill"
            ],
            menu_icon="gem",
            default_index=0,
            key="main_menu",
            styles={
                "container": {"padding": "0px", "background-color": "#1E2D3A"},
                "icon": {"color": "#4ECDC4", "font-size": "18px"},
                "nav-link": {
                    "font-size": "16px", 
                    "text-align": "left", 
                    "margin": "0px", 
                    "padding": "10px 15px",
                    "border-radius": "0px",
                    "--hover-color": "#2B3E4F"
                },
                "nav-link-selected": {
                    "background-color": "#2B3E4F", 
                    "font-weight": "bold",
                    "color": "#4ECDC4",
                    "border-left": "3px solid #4ECDC4"
                },
                "menu-title": {
                    "font-size": "22px",
                    "font-weight": "bold",
                    "margin-bottom": "10px",
                    "padding": "10px 5px",
                    "color": "#FFFFFF"
                }
            }
        )
        
        # Добавляем разделитель
        st.markdown("<hr style='margin: 20px 0; border: none; height: 1px; background-color: #2B3E4F;'>", unsafe_allow_html=True)
        
        # Добавляем информацию о версии приложения и системе
        with st.expander("Информация о системе", expanded=False):
            
            # Блок с информацией о моделях
            st.markdown("##### 🧠 Модели")
            models_list = [model_name for model_name in MODEL_CONFIG]
            columns = st.columns(2)
            for i, model in enumerate(models_list):
                col_idx = i % 2
                with columns[col_idx]:
                    st.markdown(f"<div style='background-color: #2B3E4F; padding: 5px 10px; border-radius: 5px; margin-bottom: 5px;'><small>✓ {model}</small></div>", unsafe_allow_html=True)
            
            # Информация о CUDA (если доступна)
            import torch
            if torch.cuda.is_available():
                st.markdown("##### 💻 Аппаратное обеспечение")
                device_name = torch.cuda.get_device_name(0)
                memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                
                st.markdown(f"""
                <div style='background-color: #2B3E4F; padding: 10px; border-radius: 5px; margin: 5px 0;'>
                    <div style='display: flex; justify-content: space-between;'>
                        <small>Устройство:</small>
                        <small><b>{device_name}</b></small>
                    </div>
                    <div style='display: flex; justify-content: space-between;'>
                        <small>Память:</small>
                        <small><b>{memory:.2f} ГБ</b></small>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Добавляем версию приложения в нижней части сайдбара
        st.markdown("<div style='position: absolute; bottom: 0; padding: 10px; width: 100%; text-align: center; font-size: 12px; color: #4ECDC4;'>AdsorpNET © 2025 v1.0.0</div>", unsafe_allow_html=True)
        
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
        elif selected == "AI синтез MOF":
            predict.show()
        elif selected == "О металлорганических каркасах":
            info.show()
        elif selected == "Анализ структуры":
            analysis.show()
        elif selected == "О проекте":
            team.show()
            
    except Exception as e:
        logger.error(f"Ошибка при запуске приложения: {str(e)}", exc_info=True)
        st.error(f"Произошла ошибка при запуске приложения: {str(e)}")

if __name__ == "__main__":
    run()