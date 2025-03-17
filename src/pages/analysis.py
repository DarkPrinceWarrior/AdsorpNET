"""
Страница анализа структуры MOF.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from src.utils.ui.page_config import load_theme_css

def show():
    """Отображает страницу анализа структуры."""
    load_theme_css()
    
    st.title("Анализ структуры MOF")
    
    st.markdown("""
    ### 📊 Анализ структурных характеристик
    
    Загрузите файл с данными о структуре MOF для анализа. 
    Поддерживаемые форматы: .csv, .xlsx
    """)
    
    uploaded_file = st.file_uploader("Выберите файл", type=['csv', 'xlsx'])
    
    if uploaded_file is not None:
        try:
            # Определяем тип файла и читаем данные
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.success("Файл успешно загружен!")
            
            # Показываем основные статистики
            st.subheader("Основные статистики")
            st.write(df.describe())
            
            # Выбор колонок для визуализации
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                x_col = st.selectbox("Выберите параметр для оси X:", numeric_cols)
                y_col = st.selectbox("Выберите параметр для оси Y:", numeric_cols)
                
                # Создаем график
                fig = px.scatter(df, x=x_col, y=y_col, 
                               title=f"Зависимость {y_col} от {x_col}",
                               labels={x_col: x_col, y_col: y_col})
                st.plotly_chart(fig)
                
                # Показываем корреляционную матрицу
                st.subheader("Корреляционная матрица")
                corr_matrix = df[numeric_cols].corr()
                fig_corr = px.imshow(corr_matrix,
                                   labels=dict(color="Корреляция"),
                                   x=corr_matrix.columns,
                                   y=corr_matrix.columns)
                st.plotly_chart(fig_corr)
            
            else:
                st.warning("В загруженном файле нет числовых колонок для анализа")
                
        except Exception as e:
            st.error(f"Ошибка при обработке файла: {str(e)}")
    
    st.markdown("""
    ### 📝 Рекомендации по анализу
    
    1. **Подготовка данных**:
       - Убедитесь, что данные очищены от выбросов
       - Проверьте корректность форматов данных
       
    2. **Анализ корреляций**:
       - Обратите внимание на сильные корреляции (>0.7)
       - Исследуйте отрицательные корреляции
       
    3. **Визуальный анализ**:
       - Используйте графики для выявления трендов
       - Проверьте наличие кластеров данных
    """)

    # Добавляем боковую панель с настройками
    with st.sidebar:
        st.markdown("### Настройки анализа")
        st.slider("Точность расчетов", 1, 10, 5)
        st.checkbox("Расширенный анализ")
        st.checkbox("Сохранить результаты")

if __name__ == "__main__":
    show() 