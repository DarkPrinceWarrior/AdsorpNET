"""
Страница анализа структуры MOF.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.utils.ui.page_config import load_theme_css

def show():
    """Отображает страницу аналитики MOF материалов."""
    load_theme_css()
    
    st.title("Аналитика MOF материалов")
    
    # Example dataset
    mof_data = {
        "MOF": ["MOF-5", "HKUST-1", "UiO-66", "ZIF-8", "MIL-101", "NU-1000", "MOF-74"],
        "Металл": ["Zn", "Cu", "Zr", "Zn", "Cr", "Zr", "Zn"],
        "Удельная поверхность (м²/г)": [3800, 1900, 1200, 1700, 4100, 2200, 1300],
        "Объем пор (см³/г)": [1.55, 0.75, 0.50, 0.65, 2.15, 1.40, 0.55],
        "Температурная стабильность (°C)": [400, 350, 450, 300, 300, 500, 350]
    }
    df = pd.DataFrame(mof_data)
    
    # Data exploration section
    st.markdown("### Сравнительный анализ MOF материалов")
    
    # Visualization selector
    viz_type = st.selectbox("Выберите тип визуализации", 
                           ["Удельная поверхность", "Объем пор", "Температурная стабильность", "Корреляционный анализ"])
    
    if viz_type == "Удельная поверхность":
        fig = go.Figure(go.Bar(
            x=df["MOF"],
            y=df["Удельная поверхность (м²/г)"],
            marker_color='#4e54c8',
            text=df["Удельная поверхность (м²/г)"],
            textposition='auto'
        ))
        
        fig.update_layout(
            title="Удельная поверхность различных MOF",
            xaxis_title="MOF",
            yaxis_title="Удельная поверхность (м²/г)",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    elif viz_type == "Объем пор":
        fig = go.Figure(go.Bar(
            x=df["MOF"],
            y=df["Объем пор (см³/г)"],
            marker_color='#8f94fb',
            text=df["Объем пор (см³/г)"],
            textposition='auto'
        ))
        
        fig.update_layout(
            title="Объем пор различных MOF",
            xaxis_title="MOF",
            yaxis_title="Объем пор (см³/г)",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    elif viz_type == "Температурная стабильность":
        fig = go.Figure(go.Bar(
            x=df["MOF"],
            y=df["Температурная стабильность (°C)"],
            marker_color='#5a67d8',
            text=df["Температурная стабильность (°C)"],
            textposition='auto'
        ))
        
        fig.update_layout(
            title="Температурная стабильность различных MOF",
            xaxis_title="MOF",
            yaxis_title="Температурная стабильность (°C)",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    else:  # Correlation analysis
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df["Удельная поверхность (м²/г)"],
            y=df["Объем пор (см³/г)"],
            mode='markers+text',
            text=df["MOF"],
            textposition="top center",
            marker=dict(
                size=12,
                color=df["Температурная стабильность (°C)"],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Температурная<br>стабильность (°C)")
            )
        ))
        
        fig.update_layout(
            title="Корреляция между удельной поверхностью и объемом пор",
            xaxis_title="Удельная поверхность (м²/г)",
            yaxis_title="Объем пор (см³/г)",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Data table with search
    st.markdown("### База данных MOF материалов")
    search_term = st.text_input("Поиск по MOF или металлу")
    
    if search_term:
        filtered_df = df[df.apply(lambda row: search_term.lower() in str(row["MOF"]).lower() or 
                                   search_term.lower() in str(row["Металл"]).lower(), axis=1)]
    else:
        filtered_df = df
    
    st.dataframe(filtered_df, use_container_width=True)


if __name__ == "__main__":
    show() 