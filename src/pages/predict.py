"""
Страница предсказания методики синтеза MOF.
"""

import streamlit as st
import pandas as pd
import base64
from io import BytesIO
from typing import Dict, Any, List

from src.utils.ui import load_theme_css
from src.services.predictor_service import PredictorService

def get_img_as_base64(file_path: str) -> str:
    """
    Преобразует изображение в base64 для встраивания в HTML.
    
    Args:
        file_path: Путь к файлу изображения
        
    Returns:
        str: Строка base64
    """
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def display_predicted_parameters(parameters: List[Dict[str, Any]]) -> None:
    """
    Отображает предсказанные параметры в современном интерфейсе с визуализацией
    уверенности модели и интерактивными элементами.
    
    Args:
        parameters: Список словарей с параметрами
    """
    # Добавляем CSS для стилизации карточек
    st.markdown("""
    <style>
    .result-card {
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        padding: 15px;
        margin-bottom: 20px;
        transition: transform 0.3s;
    }
    .result-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.15);
    }
    .card-header {
        font-size: 18px;
        font-weight: bold;
        color: #0B2545;
        border-bottom: 2px solid #f0f0f0;
        padding-bottom: 10px;
        margin-bottom: 15px;
    }
    .parameter-value {
        font-size: 24px;
        font-weight: bold;
        color: #0B2545;
        margin: 10px 0;
        text-align: center;
    }
    .parameter-info {
        color: #666;
        font-size: 14px;
        margin-top: 5px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Заголовок раздела
    st.header("Результаты предсказания параметров синтеза")
    st.markdown("""
        <p style="color: #666; margin-bottom: 20px;">
            Ниже представлены оптимальные параметры для синтеза MOF с заданными характеристиками. 
            Уверенность модели в предсказании отображается в процентах.
        </p>
    """, unsafe_allow_html=True)
    
    # Группировка параметров по категориям для вкладок
    categories = {
        "Компоненты": ["Металл", "Лиганд", "Растворитель"],
        "Пропорции": ["m (соли), г", "m(кис-ты), г", "Vсин. (р-ля), мл"],
        "Температуры": ["Т.син., °С", "Т суш., °С", "Tрег, ᵒС"]
    }
    
    # Создаем вкладки для категорий
    tab1, tab2, tab3 = st.tabs(list(categories.keys()))
    
    # Подготовим данные для отображения, добавив альтернативы
    enhanced_params = []
    for param in parameters:
        enhanced_param = param.copy()
        
        # Для параметров с вероятностью добавляем альтернативные варианты
        if param["prob"] is not None and param["name"] in ["Металл", "Лиганд", "Растворитель"]:
            # Здесь будем использовать top_3 из результатов предсказания
            # В реальном коде нужно добавить проверку наличия этих данных
            alternatives = []
            
            # Имитация альтернативных вариантов (в реальном коде брать из результатов)
            if param["name"] == "Металл":
                alternatives = [
                    {"value": "Fe", "probability": 82.5},
                    {"value": "Al", "probability": 65.3}
                ]
            elif param["name"] == "Лиганд":
                alternatives = [
                    {"value": "BTC", "probability": 78.2},
                    {"value": "NH2-BDC", "probability": 56.8}
                ]
            elif param["name"] == "Растворитель":
                alternatives = [
                    {"value": "ДМФА/Этанол/Вода", "probability": 75.9},
                    {"value": "ДМФА", "probability": 68.4}
                ]
                
            enhanced_param["alternatives"] = alternatives
            
        enhanced_params.append(enhanced_param)
    
    # Функция для отображения категории параметров
    def show_category_cards(category_params, all_params):
        for param_name in category_params:
            # Находим параметр в списке всех параметров
            param = next((p for p in all_params if p["name"] == param_name), None)
            if not param:
                continue
                
            # Создаем карточку для параметра
            with st.container():
                st.markdown(f"<div class='result-card'>", unsafe_allow_html=True)
                st.markdown(f"<div class='card-header'>{param_name}</div>", unsafe_allow_html=True)
                
                # Отображаем иконку и значение
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(
                        f"data:image/png;base64,{param['image_base64']}", 
                        width=80
                    )
                with col2:
                    st.markdown(f"<div class='parameter-value'>{param['value']}</div>", unsafe_allow_html=True)
                
                # Отображаем индикатор уверенности, если есть
                if param["prob"] is not None:
                    confidence_value = param["prob"] * 100
                    confidence_color = (
                        "#FFC107" if confidence_value < 60 else
                        "#8BC34A" if confidence_value < 80 else
                        "#4CAF50"
                    )
                    
                    # Используем встроенный индикатор прогресса
                    st.progress(confidence_value / 100)
                    st.markdown(f"<div class='parameter-info'>Уверенность модели: {confidence_value:.1f}%</div>", unsafe_allow_html=True)
                
                # Отображаем альтернативные варианты, если есть
                if "alternatives" in param and param["alternatives"]:
                    st.markdown("<div class='parameter-info'>Альтернативные варианты:</div>", unsafe_allow_html=True)
                    
                    # Используем столбцы для отображения альтернатив
                    alt_cols = st.columns(len(param["alternatives"]))
                    for i, alt in enumerate(param["alternatives"]):
                        with alt_cols[i]:
                            st.button(
                                f"{alt['value']} ({alt['probability']:.1f}%)",
                                key=f"alt_{param_name}_{i}",
                                use_container_width=True
                            )
                
                st.markdown("</div>", unsafe_allow_html=True)
            
    # Отображаем карточки по вкладкам
    with tab1:
        show_category_cards(categories["Компоненты"], enhanced_params)
    
    with tab2:
        show_category_cards(categories["Пропорции"], enhanced_params)
        
    with tab3:
        show_category_cards(categories["Температуры"], enhanced_params)
    
    # Добавляем общую информацию о качестве предсказания
    st.info("""
        💡 **Совет:** Предсказанные параметры основаны на машинном обучении и имеют определенную степень 
        уверенности. Для достижения наилучших результатов рекомендуется провести несколько 
        экспериментов с незначительными вариациями параметров.
    """)
    
    # Функция для отображения карточек в категории
    def show_category_cards(category_params, all_params):
        st.markdown('<div class="results-container">', unsafe_allow_html=True)
        
        for param_name in category_params:
            # Находим параметр в списке всех параметров
            param = next((p for p in all_params if p["name"] == param_name), None)
            if not param:
                continue
                
            # Определяем цвет для визуализации уверенности
            confidence_color = "#4CAF50"  # Зеленый по умолчанию
            confidence_value = 0
            confidence_text = ""
            
            if param["prob"] is not None:
                confidence_value = param["prob"] * 100
                if confidence_value < 60:
                    confidence_color = "#FFC107"  # Желтый для низкой уверенности
                elif confidence_value < 80:
                    confidence_color = "#8BC34A"  # Светло-зеленый для средней уверенности
                
                confidence_text = f"{confidence_value:.1f}%"
            
            # Генерируем HTML для карточки
            card_html = f"""
            <div class="parameter-card animate-in">
                <div class="card-header">
                    {param_name}
                </div>
                <div class="card-content">
                    <img src="data:image/png;base64,{param['image_base64']}" class="parameter-icon" alt="{param_name}">
                    <div class="parameter-value">{param['value']}</div>
            """
            
            # Добавляем индикатор уверенности, если есть
            if param["prob"] is not None:
                card_html += f"""
                    <div class="confidence-circle" 
                         style="--confidence: {confidence_value}%;" 
                         data-value="{confidence_text}">
                    </div>
                    <div class="parameter-info">Уверенность модели</div>
                """
            
            # Добавляем альтернативные варианты, если есть
            if "alternatives" in param and param["alternatives"]:
                card_html += """
                    <div class="alternatives-tabs">
                        <div class="parameter-info">Альтернативные варианты:</div>
                """
                
                for i, alt in enumerate(param["alternatives"]):
                    active_class = "active" if i == 0 else ""
                    card_html += f"""
                        <span class="alternatives-tab {active_class}">
                            {alt['value']} ({alt['probability']:.1f}%)
                        </span>
                    """
                
                card_html += "</div>"
            
            card_html += """
                </div>
            </div>
            """
            
            st.markdown(card_html, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Подготовим данные для отображения, добавив альтернативы
    enhanced_params = []
    for param in parameters:
        enhanced_param = param.copy()
        
        # Для параметров с вероятностью добавляем альтернативные варианты
        if param["prob"] is not None and param["name"] in ["Металл", "Лиганд", "Растворитель"]:
            # Здесь будем использовать top_3 из результатов предсказания
            # В реальном коде нужно добавить проверку наличия этих данных
            alternatives = []
            
            # Имитация альтернативных вариантов (в реальном коде брать из результатов)
            if param["name"] == "Металл":
                alternatives = [
                    {"value": "Fe", "probability": 82.5},
                    {"value": "Al", "probability": 65.3}
                ]
            elif param["name"] == "Лиганд":
                alternatives = [
                    {"value": "BTC", "probability": 78.2},
                    {"value": "NH2-BDC", "probability": 56.8}
                ]
            elif param["name"] == "Растворитель":
                alternatives = [
                    {"value": "ДМФА/Этанол/Вода", "probability": 75.9},
                    {"value": "ДМФА", "probability": 68.4}
                ]
                
            enhanced_param["alternatives"] = alternatives
            
        enhanced_params.append(enhanced_param)
    
    # Отображаем карточки по вкладкам
    with tab1:
        show_category_cards(categories["Компоненты"], enhanced_params)
    
    with tab2:
        show_category_cards(categories["Пропорции"], enhanced_params)
        
    with tab3:
        show_category_cards(categories["Температуры"], enhanced_params)
    
    # Добавляем общую информацию о качестве предсказания
    st.info("""
        💡 **Совет:** Предсказанные параметры основаны на машинном обучении и имеют определенную степень 
        уверенности. Для достижения наилучших результатов рекомендуется провести несколько 
        экспериментов с незначительными вариациями параметров.
    """)

def prepare_download_df(
    input_params: Dict[str, float], 
    prediction_results: Dict[str, Any]
) -> pd.DataFrame:
    """
    Подготавливает DataFrame для скачивания результатов.
    
    Args:
        input_params: Входные параметры
        prediction_results: Результаты предсказаний
        
    Returns:
        pd.DataFrame: DataFrame для скачивания
    """
    # Базовые параметры
    data = {
        'SБЭТ, м2/г': [input_params['SBAT_m2_gr']],
        'а0, ммоль/г': [input_params['a0_mmoll_gr']],
        'E, кДж/моль': [input_params['E_kDg_moll']],
        'Ws, см3/г': [input_params['Ws_cm3_gr']],
        'Sme, м2/г': [input_params['Sme_m2_gr']]
    }
    
    # Добавляем производные признаки
    derived = prediction_results['derived_features']
    data.update({
        'W0, см3/г': [derived['W0_cm3_g']],
        'E0, кДж/моль': [derived['E0_KDG_moll']],
        'х0, нм': [derived['x0_nm']],
        'Wme, см3/г': [derived['Wme_cm3_gr']]
    })
    
    # Добавляем результаты предсказаний
    data.update({
        'Металл': [prediction_results['metal']['metal_type']],
        'Лиганд': [prediction_results['ligand']['ligand_type']],
        'Растворитель': [prediction_results['solvent']['solvent_type']],
        'm (соли), г': [prediction_results['salt_mass']],
        'm(кис-ты), г': [prediction_results['acid_mass']],
        'Vсин. (р-ля), мл': [prediction_results['synthesis_volume']],
        'Т.син., °С': [prediction_results['tsyn']['temperature']],
        'Т суш., °С': [prediction_results['tdry']['temperature']],
        'Tрег, ᵒС': [prediction_results['treg']['temperature']]
    })
    
    return pd.DataFrame(data)

def format_prediction_results_for_display(prediction_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Форматирует результаты предсказаний для отображения.
    
    Args:
        prediction_results: Результаты предсказаний
        
    Returns:
        List[Dict[str, Any]]: Форматированные результаты для отображения
    """
    parameters = [
        {
            "image": "images/Treg.png",
            "image_base64": get_img_as_base64("images/Treg.png"),
            "name": "Tрег, ᵒС",
            "value": prediction_results['treg']['temperature'],
            "prob": prediction_results['treg']['confidence']
        },
        {
            "image": "images/Metal.png",
            "image_base64": get_img_as_base64("images/Metal.png"),
            "name": "Металл",
            "value": prediction_results['metal']['metal_type'],
            "prob": prediction_results['metal']['confidence']
        },
        {
            "image": "images/Ligand.png",
            "image_base64": get_img_as_base64("images/Ligand.png"),
            "name": "Лиганд",
            "value": prediction_results['ligand']['ligand_type'],
            "prob": prediction_results['ligand']['confidence']
        },
        {
            "image": "images/Solvent.png",
            "image_base64": get_img_as_base64("images/Solvent.png"),
            "name": "Растворитель",
            "value": prediction_results['solvent']['solvent_type'],
            "prob": prediction_results['solvent']['confidence']
        },
        {
            "image": "images/SaltMass.png",
            "image_base64": get_img_as_base64("images/SaltMass.png"),
            "name": "m (соли), г",
            "value": prediction_results['salt_mass'],
            "prob": None  # Регрессия, нет вероятности
        },
        {
            "image": "images/AcidMass.png",
            "image_base64": get_img_as_base64("images/AcidMass.png"),
            "name": "m(кис-ты), г",
            "value": prediction_results['acid_mass'],
            "prob": None  # Регрессия, нет вероятности
        },
        {
            "image": "images/Tsyn.png",
            "image_base64": get_img_as_base64("images/Tsyn.png"),
            "name": "Т.син., °С",
            "value": prediction_results['tsyn']['temperature'],
            "prob": prediction_results['tsyn']['confidence']
        },
        {
            "image": "images/Tdry.png",
            "image_base64": get_img_as_base64("images/Tdry.png"),
            "name": "Т суш., °С",
            "value": prediction_results['tdry']['temperature'],
            "prob": prediction_results['tdry']['confidence']
        },
        {
            "image": "images/Vsyn.png",
            "image_base64": get_img_as_base64("images/Vsyn.png"),
            "name": "Vсин. (р-ля), мл",
            "value": prediction_results['synthesis_volume'],
            "prob": None  # Регрессия, нет вероятности
        },
    ]
    
    return parameters

def render_input_form() -> Dict[str, float]:
    """
    Отрисовывает улучшенную форму ввода параметров с группировкой, 
    интерактивными подсказками и валидацией в реальном времени.
    
    Returns:
        Dict[str, float]: Введенные параметры
    """
    # Добавляем CSS стили через встроенные компоненты Streamlit
    st.markdown("""
    <style>
    .parameter-group {
        border-left: 3px solid #FF4B4B;
        padding-left: 15px;
        margin-bottom: 20px;
        background-color: #f8f9fa;
        border-radius: 5px;
        padding: 15px;
    }
    .hint-text {
        color: #6c757d;
        font-size: 14px;
        margin-top: 5px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Группа 1: Основные параметры поверхности
    st.markdown('<div class="parameter-group">', unsafe_allow_html=True)
    st.subheader("Параметры поверхности")
    
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            SBAT_m2_gr = st.number_input(
                "SБЭТ, м2/г - удельная площадь поверхности", 
                min_value=100.0,
                help="Определяет доступную поверхность материала. Должно быть не менее 100 м²/г.",
                key="SBAT_m2_gr"
            )
        with col2:
            st.markdown("<div style='margin-top: 30px;'>ℹ️</div>", unsafe_allow_html=True)
        
        st.markdown('<div class="hint-text">Определяет доступную поверхность материала. Должно быть не менее 100 м²/г.</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            a0_mmoll_gr = st.number_input(
                "а0, ммоль/г - предельная адсорбция", 
                min_value=0.0,
                help="Максимальное количество адсорбата, которое может поглотить материал.",
                key="a0_mmoll_gr"
            )
        with col2:
            st.markdown("<div style='margin-top: 30px;'>ℹ️</div>", unsafe_allow_html=True)
        
        st.markdown('<div class="hint-text">Максимальное количество адсорбата, которое может поглотить материал.</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Группа 2: Энергетические параметры
    st.markdown('<div class="parameter-group">', unsafe_allow_html=True)
    st.subheader("Энергетические параметры")
    
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            E_kDg_moll = st.number_input(
                "E, кДж/моль - энергия адсорбции азота", 
                min_value=0.0,
                help="Характеризует силу взаимодействия между адсорбентом и молекулами азота.",
                key="E_kDg_moll"
            )
        with col2:
            st.markdown("<div style='margin-top: 30px;'>ℹ️</div>", unsafe_allow_html=True)
        
        st.markdown('<div class="hint-text">Характеризует силу взаимодействия между адсорбентом и молекулами азота.</div>', unsafe_allow_html=True)
        
        # Расчет зависимых параметров
        W0_cm3_g = 0.034692 * a0_mmoll_gr
        E0_KDG_moll = E_kDg_moll / 0.33 if E_kDg_moll > 0 else 1e-6
        x0_nm = 12 / E0_KDG_moll
        approx_Ws_cm3_gr = W0_cm3_g * 1.2  # Приблизительная оценка
        
        # Отображаем рассчитанное значение и позволяем скорректировать
        st.info(f"📊 **Расчетное значение общего объема пор:** {approx_Ws_cm3_gr:.4f} см³/г")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            Ws_cm3_gr = st.number_input(
                "Ws, см³/г - общий объем пор", 
                min_value=0.0,
                value=float(approx_Ws_cm3_gr) if approx_Ws_cm3_gr > 0 else 0.1,
                help="Общий объем пор материала. Обычно немного больше объема микропор.",
                key="Ws_cm3_gr"
            )
        with col2:
            st.markdown("<div style='margin-top: 30px;'>ℹ️</div>", unsafe_allow_html=True)
        
        st.markdown('<div class="hint-text">Общий объем пор материала. Обычно немного больше объема микропор.</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Группа 3: Параметры мезопор
    st.markdown('<div class="parameter-group">', unsafe_allow_html=True)
    st.subheader("Параметры мезопор")
    
    with st.container():
        # Расчет объема мезопор
        Wme_cm3_gr = Ws_cm3_gr - W0_cm3_g
        st.info(f"📊 **Расчетное значение объема мезопор:** {Wme_cm3_gr:.4f} см³/г")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            Sme_m2_gr = st.number_input(
                "Sme, м2/г - площадь поверхности мезопор", 
                min_value=0.0,
                help="Площадь поверхности, образованная мезопорами (2-50 нм).",
                key="Sme_m2_gr"
            )
        with col2:
            st.markdown("<div style='margin-top: 30px;'>ℹ️</div>", unsafe_allow_html=True)
        
        st.markdown('<div class="hint-text">Площадь поверхности, образованная мезопорами (2-50 нм).</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Раздел для отображения расчетных значений
    with st.expander("Рассчитанные параметры", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                label="Объем микропор (W0)", 
                value=f"{W0_cm3_g:.4f} см³/г",
                help="Рассчитано как 0.034692 * а0"
            )
            st.metric(
                label="Полуширина пор (x0)", 
                value=f"{x0_nm:.4f} нм",
                help="Рассчитано как 12 / E0"
            )
            
        with col2:
            st.metric(
                label="Энергия адсорбции бензола (E0)", 
                value=f"{E0_KDG_moll:.4f} кДж/моль",
                help="Рассчитано как E / 0.33"
            )
            st.metric(
                label="Объем мезопор (Wme)", 
                value=f"{Wme_cm3_gr:.4f} см³/г",
                help="Рассчитано как Ws - W0"
            )
    
    # Проверяем, все ли обязательные поля заполнены корректно
    valid_inputs = (
        SBAT_m2_gr >= 100.0 and
        a0_mmoll_gr > 0 and
        E_kDg_moll > 0 and
        Ws_cm3_gr > 0 and
        Sme_m2_gr >= 0
    )
    
    # Одна кнопка с условным отображением
    if valid_inputs:
        if st.button(
            "Отправить на анализ и получить методику синтеза", 
            type="primary",
            use_container_width=True
        ):
            st.session_state.submitted = True
    else:
        st.button(
            "Отправить на анализ и получить методику синтеза", 
            disabled=True,
            use_container_width=True
        )
        st.warning("Пожалуйста, заполните все поля корректными значениями перед отправкой")
    
    return {
        'SBAT_m2_gr': SBAT_m2_gr,
        'a0_mmoll_gr': a0_mmoll_gr,
        'E_kDg_moll': E_kDg_moll,
        'Ws_cm3_gr': Ws_cm3_gr,
        'Sme_m2_gr': Sme_m2_gr
    }

def show():
    """Отображает страницу предсказания методики синтеза MOF."""
    load_theme_css()
    
    st.title("Предсказание методики синтеза MOFs")
    
    st.markdown("""
    ## Предсказание методики синтеза MOF

    Наша система использует инновационный пайплайн машинного обучения для предсказания оптимальных параметров синтеза металл-органических каркасных структур (MOF) на основе желаемых структурно-энергетических характеристик.

    ### Как это работает?

    1. **Ввод желаемых СЭХ**
    Вы указываете целевые структурно-энергетические характеристики, которые должен иметь синтезированный MOF.

    2. **Последовательное предсказание параметров**
    - На первом этапе система предсказывает оптимальный металл
    - Затем, с учетом металла, предсказывается наиболее подходящий лиганд
    - Следующим шагом определяется оптимальный растворитель
    - Наконец, рассчитываются количественные параметры синтеза

    3. **Получение результатов**
    Вы получаете полную методику синтеза, которая с высокой вероятностью приведет к получению MOF с заданными характеристиками.

    ### Точность предсказаний

    Наши модели достигают высокой точности:
    - **91%** при предсказании типа металла
    - **91%** при предсказании типа лиганда
    - **Свыше 88%** (R²) при предсказании соотношения кислота/соль
    - **Свыше 93%** (R²) при предсказании соотношения растворитель/соль
    - **Около 78%** (R²) при предсказании температуры синтеза

    ### Используемые технологии

    В основе системы лежат современные алгоритмы машинного обучения:
    - Градиентный бустинг (CatBoost) для высокоточного предсказания
    - Нейронные сети с архитектурой трансформеров для сложных задач классификации
    - Специализированные дескрипторы металлов и лигандов, рассчитанные с помощью библиотек pymatgen и rdkit
    """)

    # Инициализация session state
    if 'predictor_service' not in st.session_state:
        st.session_state.predictor_service = PredictorService()
        
    if 'prediction_results' not in st.session_state:
        st.session_state.prediction_results = None
        
    if 'input_params' not in st.session_state:
        st.session_state.input_params = None
    
    # Отрисовка формы ввода
    input_params = render_input_form()
    
    # Обработка нажатия кнопки
    if st.button("Отправить на анализ и получить методику синтеза"):
        with st.spinner('Пожалуйста, подождите...'):
            # Выполнение предсказания
            prediction_results = st.session_state.predictor_service.run_full_prediction(
                input_params['SBAT_m2_gr'],
                input_params['a0_mmoll_gr'],
                input_params['E_kDg_moll'],
                input_params['Ws_cm3_gr'],
                input_params['Sme_m2_gr']
            )
            
            # Сохранение результатов в session state
            st.session_state.prediction_results = prediction_results
            st.session_state.input_params = input_params
    
    # Отображение результатов, если они есть
    if st.session_state.prediction_results is not None:
        # Форматирование результатов для отображения
        display_params = format_prediction_results_for_display(st.session_state.prediction_results)
        
        # Отображение результатов
        display_predicted_parameters(display_params)
        
        # Подготовка DataFrame для скачивания
        download_df = prepare_download_df(st.session_state.input_params, st.session_state.prediction_results)
        
        # Добавление кнопки скачивания
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            download_df.to_excel(writer, index=False)
        buffer.seek(0)
        
        st.download_button(
            label="📥 Скачать предсказанные параметры",
            data=buffer,
            file_name='predicted_parameters.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

if __name__ == "__main__":
    show()