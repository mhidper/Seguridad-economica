import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import gzip
import warnings
warnings.filterwarnings('ignore')

# Configuración inicial de la página
st.set_page_config(
    page_title="Análisis de Dependencias Comerciales",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS mejorados
st.markdown("""
    <style>
        /* Estilos generales */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        .block-container {
            padding: 2rem 3rem;
            max-width: 1400px;
        }
        
        /* Título principal */
        .main-title {
            font-family: 'Inter', sans-serif;
            font-weight: 700;
            color: #1f2937;
            font-size: 2.25rem;
            margin-bottom: 2rem;
            text-align: center;
            padding: 1rem;
            background: linear-gradient(90deg, #f3f4f6 0%, #ffffff 50%, #f3f4f6 100%);
            border-radius: 12px;
        }
        
        /* Cards y contenedores */
        .stCard {
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
            background-color: white;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        
        /* Selectores */
        .stSelectbox {
            background-color: white;
            border-radius: 8px;
        }
        
        /* Métricas y estadísticas */
        .metric-container {
            background-color: #f8fafc;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
        }
        
        .metric-title {
            font-size: 1rem;
            color: #4b5563;
            margin-bottom: 0.5rem;
        }
        
        .metric-value {
            font-size: 1.5rem;
            font-weight: 600;
            color: #1f2937;
        }
        
        /* Gráficos */
        .plot-container {
            background-color: white;
            border-radius: 12px;
            padding: 1rem;
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        /* Responsividad */
        @media (max-width: 768px) {
            .block-container {
                padding: 1rem;
            }
            .main-title {
                font-size: 1.75rem;
            }
        }
    </style>
""", unsafe_allow_html=True)

def load_dependency_data():
    """
    Carga los datos de dependencias desde el archivo CSV
    """
    try:
        df = pd.read_csv('dependency_data.csv')
        return df
    except Exception as e:
        st.error(f"Error al cargar los datos de dependencias: {e}")
        return None

def load_clustering_data():
    """
    Carga los datos de clustering desde el archivo CSV
    """
    try:
        df = pd.read_csv('clustering_data.csv')
        return df
    except Exception as e:
        st.error(f"Error al cargar los datos de clustering: {e}")
        return None

def get_cluster_colors():
    """
    Define los colores para cada cluster basados en el nivel de riesgo
    """
    return {
        1: '#ef4444',  # Rojo - Alto riesgo
        0: '#f97316',  # Naranja - Riesgo medio-alto
        4: '#eab308',  # Amarillo - Riesgo medio
        2: '#22c55e',  # Verde - Riesgo bajo
        3: '#15803d',  # Verde oscuro - Riesgo muy bajo
        -1: '#94a3b8'  # Gris - Sin clasificar
    }

def create_dependency_matrix(data, country):
    """
    Crea la matriz de dependencias para un país específico
    """
    try:
        # Filtrar datos para el país seleccionado
        country_data = data[data['dependent_country'] == country]
        
        # Crear matriz pivot
        matrix = country_data.pivot(
            index='industry',
            columns='partner_country',
            values='dependency_value'
        )
        
        return matrix
    except Exception as e:
        st.error(f"Error al crear la matriz de dependencias: {e}")
        return None

def create_treemap(df, country):
    """
    Crea un treemap mejorado de las dependencias
    """
    cluster_names = {
        0: "Economías Emergentes y en Desarrollo",
        1: "Estados con Desafíos Geopolíticos",
        2: "Economías Avanzadas y Aliados Estratégicos",
        3: "Socios Históricos y Culturales",
        4: "América Latina: Aliados Regionales Clave",
        -1: "Sin Clasificar"
    }
    
    cluster_colors = get_cluster_colors()
    
    df = df.copy()
    df['cluster'] = df['cluster'].fillna(-1).astype(int)
    df['cluster_name'] = df['cluster'].map(cluster_names)
    
    fig = px.treemap(
        df,
        path=['Industry', 'cluster_name', 'Country'],
        values='Value',
        title=f'Dependencias de {country} por Industria y País',
        color='cluster_name',
        color_discrete_map={name: cluster_colors[num] for num, name in cluster_names.items()}
    )
    
    fig.update_layout(
        font_family="Inter",
        title={
            'font_size': 24,
            'font_weight': 'bold',
            'y': 0.98,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        margin=dict(t=80, l=20, r=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    
    return fig

def create_choropleth(df, country, selected_industry):
    """
    Crea un mapa coroplético mejorado
    """
    if selected_industry != 'Todas las industrias':
        map_data = df[df['Industry'] == selected_industry]
        title = f'Dependencias de {country} en {selected_industry}'
    else:
        map_data = df.groupby('Country')['Value'].mean().reset_index()
        title = f'Dependencias promedio de {country}'
    
    fig = px.choropleth(
        map_data,
        locations='Country',
        locationmode='ISO-3',
        color='Value',
        hover_name='Country',
        color_continuous_scale='RdYlBu_r',
        title=title
    )
    
    fig.update_layout(
        font_family="Inter",
        title={
            'font_size': 20,
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular',
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=60, b=0)
    )
    
    return fig

def display_statistics(viz_data, selected_industry):
    """
    Muestra estadísticas mejoradas con mejor visualización
    """
    st.markdown('<div class="stCard">', unsafe_allow_html=True)
    
    cols = st.columns(3)
    
    with cols[0]:
        st.markdown("### 📊 Estadísticas Generales")
        total_dep = viz_data['Value'].sum()
        
        st.markdown(
            f'''
            <div class="metric-container">
                <div class="metric-title">Dependencia Total</div>
                <div class="metric-value">{total_dep:.3f}</div>
            </div>
            ''',
            unsafe_allow_html=True
        )
        
        if selected_industry != 'Todas las industrias':
            mean_dep = viz_data['Value'].mean()
            max_dep = viz_data['Value'].max()
            
            st.markdown(
                f'''
                <div class="metric-container">
                    <div class="metric-title">Dependencia Media</div>
                    <div class="metric-value">{mean_dep:.3f}</div>
                </div>
                <div class="metric-container">
                    <div class="metric-title">Dependencia Máxima</div>
                    <div class="metric-value">{max_dep:.3f}</div>
                </div>
                ''',
                unsafe_allow_html=True
            )
    
    with cols[1]:
        st.markdown("### 🔝 Principales Dependencias")
        top_deps = viz_data.nlargest(5, 'Value')
        
        for _, row in top_deps.iterrows():
            st.markdown(
                f'''
                <div class="metric-container">
                    <div class="metric-title">{row["Country"]}</div>
                    <div class="metric-value">{row["Value"]:.3f}</div>
                    <div style="color: #6b7280; font-size: 0.875rem;">
                        {row["cluster_name"]}
                    </div>
                </div>
                ''',
                unsafe_allow_html=True
            )
    
    with cols[2]:
        st.markdown("### 📈 Análisis por Cluster")
        
        cluster_stats = viz_data.groupby('cluster_name')['Value'].agg(['sum', 'count']).round(3)
        cluster_stats['percentage'] = (cluster_stats['sum'] / total_dep * 100).round(2)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=cluster_stats.index,
            x=cluster_stats['percentage'],
            orientation='h',
            marker_color=[get_cluster_colors().get(i, '#94a3b8') for i in range(len(cluster_stats))]
        ))
        
        fig.update_layout(
            title="Distribución por Cluster (%)",
            font_family="Inter",
            showlegend=False,
            margin=dict(l=0, r=0, t=30, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    """
    Función principal de la aplicación
    """
    st.markdown('<h1 class="main-title">Análisis de Dependencias Comerciales</h1>', unsafe_allow_html=True)
    
    try:
        # Cargar datos
        data = load_dependency_data()
        clustering_data = load_clustering_data()
        
        if data is None or clustering_data is None:
            st.error("⚠️ Error al cargar los datos. Verifique los archivos de entrada.")
            return
        
        # Contenedor para selectores
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        cols = st.columns(2)
        
        with cols[0]:
            countries = sorted(data['dependent_country'].unique())
            default_country = 'ESP' if 'ESP' in countries else countries[0]
            selected_country = st.selectbox(
                '🌍 Seleccione un país para analizar:',
                countries,
                index=countries.index(default_country)
            )
        
        if selected_country:
            matrix = create_dependency_matrix(data, selected_country)
            
            if matrix is None or matrix.empty:
                st.error(f"No hay datos disponibles para {selected_country}")
                return
            
            with cols[1]:
                industries = ['Todas las industrias'] + list(matrix.index)
                selected_industry = st.selectbox(
                    '🏭 Seleccione una industria:',
                    industries
                )
        
            # Crear pestañas para visualizaciones
            tabs = st.tabs(["🗺️ Mapa Mundial", "🌳 Árbol de Dependencias"])
            
            with tabs[0]:
                try:
                    map_fig = create_choropleth(matrix, selected_country, selected_industry)
                    st.plotly_chart(map_fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Error al crear el mapa: {e}")
            
            with tabs[1]:
                try:
                    tree_fig = create_treemap(matrix, selected_country)
                    st.plotly_chart(tree_fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Error al crear el árbol de dependencias: {e}")
            
            # Mostrar estadísticas
            try:
                display_statistics(matrix, selected_industry)
            except Exception as e:
                st.error(f"Error al mostrar las estadísticas: {e}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error inesperado: {e}")

if __name__ == '__main__':
    main()