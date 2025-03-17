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
    Отображает предсказанные параметры в виде сетки.
    
    Args:
        parameters: Список словарей с параметрами
    """
    st.markdown(
        """
        <style>
        .parameter-card {
            border: 2px solid #000000;
            border-radius: 10px;
            padding: 10px;
            background-color: #FFFFFF;
            text-align: center;
            height: 180px;
        }
        .parameter-name {
            color: #000000;
            font-weight: bold;
            margin-top: 10px;
        }
        .parameter-value {
            color: #000000;
            margin-top: 5px;
            font-size: 18px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # st.header("Предсказанные Параметры Синтеза MOF Адсорбента")
    # st.markdown("---")
    
    rows = [parameters[i:i + 5] for i in range(0, len(parameters), 5)]
    
    for row in rows:
        cols = st.columns(len(row))
        for col, param in zip(cols, row):
            with col:
                param_html = f"""
                <div class="parameter-card">
                    <img src="data:image/png;base64,{param['image_base64']}" width="81" height="81">
                    <div class="parameter-name">{param['name']}</div>
                    <div class="parameter-value">{param['value']}"""
                
                if param['prob'] is not None:
                    param_html += f""" (Вероятность: {param['prob']*100:.1f}%)"""
                
                param_html += """</div></div>"""
                st.markdown(param_html, unsafe_allow_html=True)
        st.markdown("")

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
    Отрисовывает форму ввода параметров и возвращает введенные значения.
    
    Returns:
        Dict[str, float]: Введенные параметры
    """
    # Ввод пользовательских параметров
    SBAT_m2_gr = st.number_input("SБЭТ, м2/г - удельная площадь поверхности", min_value=100.0)
    a0_mmoll_gr = st.number_input("а0, ммоль/г - предельная адсорбция", min_value=0.0)
    E_kDg_moll = st.number_input("E, кДж/моль - энергия адсорбции азота", min_value=0.0)
    
    # Расчет зависимых параметров
    W0_cm3_g = 0.034692 * a0_mmoll_gr
    E0_KDG_moll = E_kDg_moll / 0.33 if E_kDg_moll > 0 else 1e-6
    x0_nm = 12 / E0_KDG_moll
    approx_Ws_cm3_gr = a0_mmoll_gr * 0.034692
    
    Ws_cm3_gr = st.number_input(
        f"Ws, см³/г - общий объем пор (приблизительное значение: {approx_Ws_cm3_gr:.4f} см³/г)", 
        min_value=0.0
    )
    
    Wme_cm3_gr = Ws_cm3_gr - W0_cm3_g
    Sme_m2_gr = st.number_input("Sme, м2/г - площадь поверхности мезопор")

    # Вывод расчетных значений
    with st.expander("Показать расчетные значения"):
        st.write(f"Объем микропор (W0): {W0_cm3_g:.4f} см³/г")
        st.write(f"Энергия адсорбции по бензолу (E0): {E0_KDG_moll:.4f} кДж/моль")
        st.write(f"Полуширина пор (x0): {x0_nm:.4f} нм")
        st.write(f"Объем мезопор (Wme): {Wme_cm3_gr:.4f} см³/г")
    
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