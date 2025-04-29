"""
Страница анализа структуры MOF.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from src.utils.ui.page_config import load_theme_css

def show():
    """Отображает улучшенную страницу анализа структуры с интерактивными графиками."""
    load_theme_css()
    
    st.title("Анализ структуры MOF")
    
    # Обновленный интерфейс с боковой панелью и основной областью
    col_sidebar, col_main = st.columns([1, 3])
    
    with col_sidebar:
        st.markdown("""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
            <h4 style="margin-top: 0;">Параметры анализа</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Загрузка файла с улучшенным интерфейсом
        uploaded_file = st.file_uploader(
            "Выберите файл", 
            type=['csv', 'xlsx'],
            help="Поддерживаются форматы CSV и Excel"
        )
        
        # Добавляем опции анализа
        if uploaded_file is not None:
            st.markdown("### Настройки анализа")
            
            # Выбор типа анализа
            analysis_type = st.radio(
                "Тип анализа",
                ["Корреляционный анализ", "Кластерный анализ", "Распределение значений"]
            )
            
            # Настройки визуализации
            st.markdown("### Настройки визуализации")
            plot_theme = st.selectbox(
                "Тема графиков",
                ["Светлая", "Темная", "Голубая", "Красная"]
            )
            
            show_legend = st.checkbox("Показать легенду", value=True)
            show_grid = st.checkbox("Показать сетку", value=True)
            
            # Кнопка для запуска анализа
            analyze_button = st.button("Запустить анализ", type="primary", use_container_width=True)
            
            # Экспорт результатов
            if 'df' in st.session_state:
                export_format = st.selectbox(
                    "Формат экспорта",
                    ["Excel (.xlsx)", "CSV (.csv)", "JSON (.json)"]
                )
                
                st.download_button(
                    label="Скачать результаты",
                    data=get_download_data(st.session_state.df, export_format),
                    file_name=f"mof_analysis_results.{export_format.split('.')[-1].lower()}",
                    mime=get_mime_type(export_format),
                    use_container_width=True
                )
    
    with col_main:
        if uploaded_file is None:
            # Показываем информацию и примеры, когда файл не загружен
            st.markdown("""
            <div style="text-align: center; padding: 40px 20px; background-color: #f8f9fa; border-radius: 10px;">
                <img src="https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/svg/1f4ca.svg" width="80" height="80">
                <h2 style="margin-top: 20px;">Загрузите файл для анализа</h2>
                <p style="color: #6c757d; max-width: 500px; margin: 0 auto;">
                    Загрузите файл CSV или Excel, содержащий данные о структурно-энергетических характеристиках MOF.
                    После загрузки вы сможете выполнить различные виды анализа и визуализации данных.
                </p>
            </div>
            
            <div style="margin-top: 30px;">
                <h3>Возможности анализа</h3>
                <div style="display: flex; gap: 20px; flex-wrap: wrap; margin-top: 20px;">
                    <div style="flex: 1; min-width: 250px; padding: 20px; background-color: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <h4>Корреляционный анализ</h4>
                        <p>Выявление взаимосвязей между различными параметрами MOF.</p>
                    </div>
                    <div style="flex: 1; min-width: 250px; padding: 20px; background-color: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <h4>Кластерный анализ</h4>
                        <p>Группировка MOF по схожим характеристикам.</p>
                    </div>
                    <div style="flex: 1; min-width: 250px; padding: 20px; background-color: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <h4>Распределение значений</h4>
                        <p>Анализ распределения ключевых параметров.</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            try:
                # Определяем тип файла и читаем данные
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                # Сохраняем DataFrame в session_state для доступа в других частях приложения
                st.session_state.df = df
                
                # Показываем сводную информацию о данных
                with st.expander("Обзор данных", expanded=True):
                    st.markdown("""
                    <style>
                    .dataframe-container {
                        border-radius: 10px;
                        overflow: hidden;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    
                    # Статистика данных
                    data_info = {
                        "Количество образцов": len(df),
                        "Количество параметров": len(df.columns),
                        "Пропущенные значения": df.isna().sum().sum(),
                        "Числовые колонки": len(df.select_dtypes(include=[np.number]).columns),
                        "Нечисловые колонки": len(df.select_dtypes(exclude=[np.number]).columns)
                    }
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### Общая информация")
                        for key, value in data_info.items():
                            st.markdown(f"**{key}:** {value}")
                    
                    with col2:
                        st.markdown("#### Основные статистики")
                        if not df.empty and len(df.select_dtypes(include=[np.number]).columns) > 0:
                            stats_df = df.describe().T[["mean", "std", "min", "max"]]
                            stats_df = stats_df.rename(columns={
                                "mean": "Среднее",
                                "std": "Ст. отклонение",
                                "min": "Минимум",
                                "max": "Максимум"
                            })
                            st.dataframe(stats_df.style.format("{:.3f}"), use_container_width=True)
                        else:
                            st.info("Нет числовых данных для отображения статистик")
                    
                    st.markdown("#### Предварительный просмотр данных")
                    st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
                    st.dataframe(df.head(10), use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Анализ колонок
                    st.markdown("#### Типы колонок и пропущенные значения")
                    column_info = get_column_info(df)
                    st.dataframe(column_info, use_container_width=True)
                
                # Выбор колонок для визуализации
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                if len(numeric_cols) > 0:
                    # Корреляционный анализ
                    if analysis_type == "Корреляционный анализ":
                        st.markdown("## Корреляционный анализ")
                        
                        # Выбор параметров для анализа
                        selected_cols = st.multiselect(
                            "Выберите параметры для анализа",
                            options=numeric_cols,
                            default=numeric_cols[:min(5, len(numeric_cols))]
                        )
                        
                        if len(selected_cols) >= 2:
                            # Создаем интерактивную тепловую карту корреляций
                            st.markdown("### Матрица корреляций")
                            
                            cols_for_corr, corr_matrix = safe_correlation_matrix(df[selected_cols])
                            
                            # Создаем интерактивную тепловую карту с Plotly
                            fig_corr = px.imshow(
                            corr_matrix,
                            x=cols_for_corr,
                            y=cols_for_corr,
                            zmin=-1, zmax=1,
                            color_continuous_scale="RdBu_r" if plot_theme in ["Светлая", "Голубая"] else "RdBu",
                            labels=dict(color="Коэффициент\nкорреляции"),
                            title="Матрица корреляции Пирсона"
                                )
                            
                            # Настройки внешнего вида
                            fig_corr.update_layout(
                                template="plotly_white" if plot_theme == "Светлая" else 
                                         "plotly_dark" if plot_theme == "Темная" else
                                         "plotly" if plot_theme == "Голубая" else "plotly_white",
                                showlegend=show_legend,
                                width=700,
                                height=700
                            )
                            
                            if show_grid:
                                fig_corr.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.1)')
                                fig_corr.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.1)')
                            
                            # Добавляем аннотации с точными значениями
                            annotations = []
                            for i, row in enumerate(corr_matrix.index):
                                for j, col in enumerate(corr_matrix.columns):
                                    annotations.append(
                                        dict(
                                            x=j, y=i,
                                            text=f"{corr_matrix.iloc[i, j]:.2f}",
                                            showarrow=False,
                                            font=dict(
                                                color="white" if abs(corr_matrix.iloc[i, j]) > 0.5 else "black"
                                            )
                                        )
                                    )
                            fig_corr.update_layout(annotations=annotations)
                            
                            st.plotly_chart(fig_corr, use_container_width=True)
                            
                            # Добавляем интерактивный scatter plot для выбранных параметров
                            st.markdown("### Диаграмма рассеяния")
                            x_col = st.selectbox("Параметр X", options=selected_cols, index=0)
                            y_col = st.selectbox("Параметр Y", options=[c for c in selected_cols if c != x_col], 
                                                index=min(1, len(selected_cols)-1))
                            
                            color_col = st.selectbox(
                                "Цветовая дифференциация (опционально)", 
                                options=["Нет"] + df.columns.tolist(),
                                index=0
                            )
                            
                            fig_scatter = px.scatter(
                                df,
                                x=x_col,
                                y=y_col,
                                color=None if color_col == "Нет" else color_col,
                                opacity=0.7,
                                trendline="ols" if st.checkbox("Показать линию тренда", value=True) else None,
                                title=f"Зависимость {y_col} от {x_col}",
                                hover_data=df.columns[:5].tolist(),
                                labels={x_col: x_col, y_col: y_col}
                            )
                            
                            # Настройки внешнего вида
                            fig_scatter.update_layout(
                                template="plotly_white" if plot_theme == "Светлая" else 
                                         "plotly_dark" if plot_theme == "Темная" else
                                         "plotly" if plot_theme == "Голубая" else "plotly_white",
                                showlegend=show_legend,
                                width=700,
                                height=500
                            )
                            
                            if show_grid:
                                fig_scatter.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.1)')
                                fig_scatter.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.1)')
                            
                            st.plotly_chart(fig_scatter, use_container_width=True)
                            
                            # Выводим статистику корреляции
                            corr_value = df[x_col].corr(df[y_col])
                            st.markdown(f"""
                            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; margin-top: 20px;">
                                <h4 style="margin-top: 0;">Статистика корреляции</h4>
                                <p><strong>Коэффициент корреляции Пирсона:</strong> {corr_value:.4f}</p>
                                <p><strong>Интерпретация:</strong> {
                                    "Сильная положительная корреляция" if corr_value > 0.7 else
                                    "Умеренная положительная корреляция" if corr_value > 0.4 else
                                    "Слабая положительная корреляция" if corr_value > 0.1 else
                                    "Сильная отрицательная корреляция" if corr_value < -0.7 else
                                    "Умеренная отрицательная корреляция" if corr_value < -0.4 else
                                    "Слабая отрицательная корреляция" if corr_value < -0.1 else
                                    "Корреляция отсутствует"
                                }</p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.warning("Выберите не менее двух параметров для анализа корреляций")
                    
                    # Кластерный анализ
                    elif analysis_type == "Кластерный анализ":
                        st.markdown("## Кластерный анализ")
                        
                        # Выбор параметров для кластеризации
                        clustering_cols = st.multiselect(
                            "Выберите параметры для кластеризации",
                            options=numeric_cols,
                            default=numeric_cols[:min(3, len(numeric_cols))]
                        )
                        
                        if len(clustering_cols) >= 2:
                            n_clusters = st.slider("Количество кластеров", min_value=2, max_value=10, value=3)
                            
                            # Создаем модель K-means
                            from sklearn.cluster import KMeans
                            from sklearn.preprocessing import StandardScaler
                            
                            # Масштабируем данные
                            scaler = StandardScaler()
                            scaled_data = scaler.fit_transform(df[clustering_cols])
                            
                            # Применяем K-means
                            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                            df['cluster'] = kmeans.fit_predict(scaled_data)
                            
                            # Создаем 3D визуализацию кластеров для первых трех параметров
                            if len(clustering_cols) >= 3:
                                st.markdown("### 3D визуализация кластеров")
                                
                                x_col = clustering_cols[0]
                                y_col = clustering_cols[1]
                                z_col = clustering_cols[2]
                                
                                fig_3d = px.scatter_3d(
                                    df,
                                    x=x_col,
                                    y=y_col,
                                    z=z_col,
                                    color='cluster',
                                    color_continuous_scale='Viridis' if plot_theme != "Красная" else 'Reds',
                                    opacity=0.7,
                                    title=f"3D визуализация кластеров ({x_col}, {y_col}, {z_col})",
                                    labels={
                                        'cluster': 'Кластер',
                                        x_col: x_col,
                                        y_col: y_col,
                                        z_col: z_col
                                    }
                                )
                                
                                # Настройки внешнего вида
                                fig_3d.update_layout(
                                    template="plotly_white" if plot_theme == "Светлая" else 
                                             "plotly_dark" if plot_theme == "Темная" else
                                             "plotly" if plot_theme == "Голубая" else "plotly_white",
                                    showlegend=show_legend,
                                    width=700,
                                    height=700
                                )
                                
                                st.plotly_chart(fig_3d, use_container_width=True)
                            
                            # Создаем 2D визуализацию кластеров
                            st.markdown("### 2D визуализация кластеров")
                            
                            x_col = st.selectbox("Параметр X", options=clustering_cols, index=0)
                            y_col = st.selectbox("Параметр Y", options=[c for c in clustering_cols if c != x_col], 
                                                index=min(1, len(clustering_cols)-1))
                            
                            fig_cluster = px.scatter(
                                df,
                                x=x_col,
                                y=y_col,
                                color='cluster',
                                color_continuous_scale='Viridis' if plot_theme != "Красная" else 'Reds',
                                opacity=0.7,
                                title=f"Кластеризация по параметрам {x_col} и {y_col}",
                                hover_data=clustering_cols,
                                labels={
                                    'cluster': 'Кластер',
                                    x_col: x_col,
                                    y_col: y_col
                                }
                            )
                            
                            # Добавляем центроиды кластеров
                            centers = kmeans.cluster_centers_
                            centers_df = pd.DataFrame(scaler.inverse_transform(centers), columns=clustering_cols)
                            
                            for i in range(n_clusters):
                                fig_cluster.add_trace(
                                    go.Scatter(
                                        x=[centers_df.loc[i, x_col]],
                                        y=[centers_df.loc[i, y_col]],
                                        mode='markers',
                                        marker=dict(
                                            symbol='star',
                                            size=15,
                                            color=i,
                                            colorscale='Viridis' if plot_theme != "Красная" else 'Reds',
                                            line=dict(color='black', width=1)
                                        ),
                                        name=f'Центроид кластера {i}'
                                    )
                                )
                            
                            # Настройки внешнего вида
                            fig_cluster.update_layout(
                                template="plotly_white" if plot_theme == "Светлая" else 
                                         "plotly_dark" if plot_theme == "Темная" else
                                         "plotly" if plot_theme == "Голубая" else "plotly_white",
                                showlegend=show_legend,
                                width=700,
                                height=500
                            )
                            
                            if show_grid:
                                fig_cluster.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.1)')
                                fig_cluster.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.1)')
                            
                            st.plotly_chart(fig_cluster, use_container_width=True)
                            
                            # Статистика по кластерам
                            st.markdown("### Статистика по кластерам")
                            
                            cluster_stats = df.groupby('cluster')[clustering_cols].mean()
                            
                            # Создаем радарный график для сравнения кластеров
                            fig_radar = go.Figure()
                            
                            for i in range(n_clusters):
                                # Нормализуем значения для радарного графика
                                values = []
                                for col in clustering_cols:
                                    min_val = df[col].min()
                                    max_val = df[col].max()
                                    if max_val > min_val:
                                        normalized = (cluster_stats.loc[i, col] - min_val) / (max_val - min_val)
                                    else:
                                        normalized = 0.5
                                    values.append(normalized)
                                
                                fig_radar.add_trace(go.Scatterpolar(
                                    r=values,
                                    theta=clustering_cols,
                                    fill='toself',
                                    name=f'Кластер {i}'
                                ))
                            
                            fig_radar.update_layout(
                                polar=dict(
                                    radialaxis=dict(
                                        visible=True,
                                        range=[0, 1]
                                    )
                                ),
                                title="Сравнение характеристик кластеров (нормализованные значения)",
                                template="plotly_white" if plot_theme == "Светлая" else 
                                         "plotly_dark" if plot_theme == "Темная" else
                                         "plotly" if plot_theme == "Голубая" else "plotly_white",
                                showlegend=show_legend
                            )
                            
                            st.plotly_chart(fig_radar, use_container_width=True)
                            
                            # Таблица со статистикой по кластерам
                            st.markdown("#### Средние значения параметров по кластерам")
                            st.dataframe(cluster_stats.style.format("{:.3f}"), use_container_width=True)
                            
                            # Размеры кластеров
                            cluster_sizes = df['cluster'].value_counts().sort_index()
                            
                            fig_sizes = px.bar(
                                x=cluster_sizes.index,
                                y=cluster_sizes.values,
                                title="Размеры кластеров",
                                labels={'x': 'Кластер', 'y': 'Количество объектов'},
                                color=cluster_sizes.index,
                                color_continuous_scale='Viridis' if plot_theme != "Красная" else 'Reds',
                            )
                            
                            fig_sizes.update_layout(
                                template="plotly_white" if plot_theme == "Светлая" else 
                                         "plotly_dark" if plot_theme == "Темная" else
                                         "plotly" if plot_theme == "Голубая" else "plotly_white",
                                showlegend=False
                            )
                            
                            st.plotly_chart(fig_sizes, use_container_width=True)
                        else:
                            st.warning("Выберите не менее двух параметров для кластерного анализа")
                    
                    # Распределение значений
                    elif analysis_type == "Распределение значений":
                        st.markdown("## Распределение значений")
                        
                        # Выбор параметров для анализа распределения
                        dist_col = st.selectbox(
                            "Выберите параметр для анализа распределения",
                            options=numeric_cols
                        )
                        
                        # Создаем гистограмму и KDE
                        st.markdown("### Гистограмма и плотность распределения")
                        
                        fig_hist = px.histogram(
                            df,
                            x=dist_col,
                            marginal="box",
                            title=f"Распределение параметра {dist_col}",
                            histnorm="probability density",
                            labels={dist_col: dist_col},
                            color_discrete_sequence=['#0B2545'] if plot_theme == "Светлая" else 
                                                    ['#D3D3D3'] if plot_theme == "Темная" else
                                                    ['#1F77B4'] if plot_theme == "Голубая" else
                                                    ['#FF4B4B']
                        )
                        
                        # Настройки внешнего вида
                        fig_hist.update_layout(
                            template="plotly_white" if plot_theme == "Светлая" else 
                                     "plotly_dark" if plot_theme == "Темная" else
                                     "plotly" if plot_theme == "Голубая" else "plotly_white",
                            showlegend=show_legend,
                            width=700,
                            height=500
                        )
                        
                        if show_grid:
                            fig_hist.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.1)')
                            fig_hist.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.1)')
                        
                        st.plotly_chart(fig_hist, use_container_width=True)
                        
                        # Статистика распределения
                        st.markdown("### Статистика распределения")
                        
                        # Базовая статистика
                        dist_stats = df[dist_col].describe()
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("#### Основные статистики")
                            stats_data = {
                                "Показатель": ["Среднее", "Медиана", "Стандартное отклонение", "Минимум", "Максимум"],
                                "Значение": [
                                    f"{dist_stats['mean']:.4f}",
                                    f"{dist_stats['50%']:.4f}",
                                    f"{dist_stats['std']:.4f}",
                                    f"{dist_stats['min']:.4f}",
                                    f"{dist_stats['max']:.4f}"
                                ]
                            }
                            st.dataframe(pd.DataFrame(stats_data), use_container_width=True)
                        
                        with col2:
                            st.markdown("#### Квантили")
                            quantiles = [0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99]
                            quantile_values = [df[dist_col].quantile(q) for q in quantiles]
                            
                            quantile_data = {
                                "Квантиль": [f"{q*100}%" for q in quantiles],
                                "Значение": [f"{val:.4f}" for val in quantile_values]
                            }
                            st.dataframe(pd.DataFrame(quantile_data), use_container_width=True)
                        
                        # График квантилей (QQ-plot)
                        st.markdown("### График квантилей (QQ-plot)")
                        
                        from scipy import stats
                        
                        # Вычисляем теоретические квантили для нормального распределения
                        sorted_data = sorted(df[dist_col].dropna())
                        norm_quantiles = [stats.norm.ppf((i+0.5)/len(sorted_data)) for i in range(len(sorted_data))]
                        
                        # Создаем QQ-plot
                        fig_qq = px.scatter(
                            x=norm_quantiles,
                            y=sorted_data,
                            title=f"QQ-plot для параметра {dist_col}",
                            labels={"x": "Теоретические квантили", "y": dist_col}
                        )
                        
                        # Добавляем линию нормального распределения
                        min_val = min(norm_quantiles)
                        max_val = max(norm_quantiles)
                        min_data = min(sorted_data)
                        max_data = max(sorted_data)
                        
                        fig_qq.add_trace(
                            go.Scatter(
                                x=[min_val, max_val],
                                y=[min_data, max_data],
                                mode="lines",
                                line=dict(color="red", dash="dash"),
                                name="Нормальное распределение"
                            )
                        )
                        
                        # Настройки внешнего вида
                        fig_qq.update_layout(
                            template="plotly_white" if plot_theme == "Светлая" else 
                                     "plotly_dark" if plot_theme == "Темная" else
                                     "plotly" if plot_theme == "Голубая" else "plotly_white",
                            showlegend=show_legend,
                            width=700,
                            height=500
                        )
                        
                        if show_grid:
                            fig_qq.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.1)')
                            fig_qq.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.1)')
                        
                        st.plotly_chart(fig_qq, use_container_width=True)
                        
                        # Тест на нормальность
                        st.markdown("### Тест на нормальность распределения")
                        
                        from scipy import stats
                        
                        alpha = 0.05
                        stat, p = stats.shapiro(df[dist_col].dropna())
                        
                        st.markdown(f"""
                        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; margin-top: 20px;">
                            <h4 style="margin-top: 0;">Результаты теста Шапиро-Уилка</h4>
                            <p><strong>Статистика:</strong> {stat:.4f}</p>
                            <p><strong>p-значение:</strong> {p:.4f}</p>
                            <p><strong>Вывод:</strong> {
                                f"Распределение параметра {dist_col} значимо отличается от нормального (p < {alpha})" 
                                if p < alpha else
                                f"Нет оснований отвергать гипотезу о нормальности распределения параметра {dist_col} (p > {alpha})"
                            }</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("В загруженном файле нет числовых колонок для анализа")
            except Exception as e:
                st.error(f"Ошибка при обработке файла: {str(e)}")
                st.exception(e)

# Вспомогательные функции для экспорта данных
def get_download_data(df, format_type):
    """Подготавливает данные для скачивания в выбранном формате."""
    from io import BytesIO
    
    buffer = BytesIO()
    
    if format_type == "Excel (.xlsx)":
        df.to_excel(buffer, index=False)
    elif format_type == "CSV (.csv)":
        df.to_csv(buffer, index=False)
    elif format_type == "JSON (.json)":
        buffer.write(df.to_json(orient="records").encode())
    
    buffer.seek(0)
    return buffer

def get_mime_type(format_type):
    """Возвращает MIME-тип для выбранного формата файла."""
    if format_type == "Excel (.xlsx)":
        return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif format_type == "CSV (.csv)":
        return "text/csv"
    elif format_type == "JSON (.json)":
        return "application/json"
    return "application/octet-stream"


def get_column_info(df):
    """
    Получает информацию о колонках DataFrame с правильными типами данных для отображения.
    
    Args:
        df: pandas DataFrame
        
    Returns:
        pd.DataFrame: Информация о колонках
    """
    # Создаем новый DataFrame для хранения информации о колонках
    data = {
        'Тип данных (строка)': [str(dtype) for dtype in df.dtypes],
        'Пропущенные значения': df.isna().sum(),
        '% пропущенных': (df.isna().sum() / len(df) * 100).round(2)
    }
    return pd.DataFrame(data)


# Для безопасной визуализации корреляций
def safe_correlation_matrix(df):
    """
    Создает безопасную матрицу корреляций для визуализации.
    
    Args:
        df: pandas DataFrame
        
    Returns:
        np.ndarray: Матрица корреляций
    """
    # Берем только числовые колонки
    numeric_df = df.select_dtypes(include=[np.number])
    
    # Выполняем корреляцию и конвертируем в numpy array
    corr_matrix = numeric_df.corr().values
    
    # Возвращаем имена колонок и матрицу
    return numeric_df.columns.tolist(), corr_matrix


if __name__ == "__main__":
    show() 