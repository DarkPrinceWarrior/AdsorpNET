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
    """Создает боковое меню навигации."""
    with st.sidebar:
        selected = option_menu(
            menu_title="𝐀𝐈 сервис пористых материалов",
            options=["О нас", "MOFs описание", "𝐀𝐈 синтез MOFs", "Анализ структуры", "Контакты"],
            icons=["house", "book", "box fill", "search", "person lines fill"],
            menu_icon="kanban fill",
            default_index=0,
            key="main_menu",
            styles={
                "container": {"padding": "0 % 0 % 0 % 0 %"},
                "icon": {"color": "red", "font-size": "25px"},
                "nav-link": {"font-size": "20px", "text-align": "start", "margin": "0px"},
                "nav-link-selected": {"background-color": "#483D8B"},
            }
        )
        
        # Добавляем информацию о моделях
        if st.session_state.get('model_service'):
            with st.expander("Информация о системе", expanded=False):
                st.write("### Модели")
                for model_name in MODEL_CONFIG:
                    st.write(f"✓ {model_name}")
                
                # Добавим статистику CUDA если доступна
                import torch
                if torch.cuda.is_available():
                    st.write("### CUDA")
                    st.write(f"Устройство: {torch.cuda.get_device_name(0)}")
                    memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                    st.write(f"Память: {memory:.2f} ГБ")
        
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
        
        # Инициализируем сервисы
        initialize_services()
        
        # Создаем боковое меню и получаем выбранный пункт
        selected = create_sidebar()
        
        # Выбор и отображение страницы
        if selected == "О нас":
            home.show()
        elif selected == "𝐀𝐈 синтез MOFs":
            predict.show()
        elif selected == "MOFs описание":
            info.show()
        elif selected == "Анализ структуры":
            analysis.show()
        elif selected == "Контакты":
            team.show()
            
    except Exception as e:
        logger.error(f"Ошибка при запуске приложения: {str(e)}", exc_info=True)
        st.error(f"Произошла ошибка при запуске приложения: {str(e)}")

if __name__ == "__main__":
    run()