import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import gzip
from load_data import load_dependency_data, load_clustering_data, build_dependency_matrix, process_data_for_visualization

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Dependencias Comerciales",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado mejorado
st.markdown("""
    <style>
        /* Estilos generales y fuentes */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        .block-container {
            padding: 2rem 3rem;
            max-width: 1400px;
        }
        
        /* Estilo para el título principal */
        .main-title {
            font-family: 'Inter', sans-serif;
            font-weight: 700;
            color: #1f2937;
            font-size: 2.25rem;
            margin-bottom: 2rem;
            text-align: center;
        }
        
        /* Estilos para las cards */
        .stCard {
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
            background-color: white;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        
        /* Estilos para selectboxes */
        .stSelectbox {
            background-color: white;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
        }
        
        /* Estilos para tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
            background-color: transparent;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 3rem;
            padding: 0 1.5rem;
            font-weight: 500;
            background-color: transparent;
            border-radius: 8px;
        }
        
        /* Estilos para gráficos */
        .plot-container {
            border-radius: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            background-color: white;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        /* Estilos para métricas */
        .metric-card {
            background-color: #f8fafc;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
        }
        
        /* Estilos para tablas */
        .dataframe {
            border-radius: 8px !important;
            overflow: hidden;
        }
        
        .dataframe th {
            background-color: #f8fafc !important;
            font-weight: 600 !important;
        }
        
        /* Responsive design */
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

def get_cluster_colors():
    """Define colores mejorados para cada cluster"""
    return {
        1: '#ef4444',  # Rojo más vibrante
        0: '#f97316',  # Naranja más vibrante
        4: '#eab308',  # Amarillo más vibrante
        2: '#22c55e',  # Verde más vibrante
        3: '#15803d'   # Verde oscuro más vibrante
    }

def create_treemap(df, country):
    """Treemap mejorado con mejor diseño visual"""
    cluster_names = {
        0: "Economías Emergentes y en Desarrollo",
        1: "Estados con Desafíos Geopolíticos",
        2: "Economías Avanzadas y Aliados Estratégicos",
        3: "Socios Históricos y Culturales",
        4: "América Latina: Aliados Regionales Clave",
        -1: "Sin Clasificar"
    }
    
    cluster_colors = get_cluster_colors()
    cluster_colors[-1] = '#94a3b8'  # Gris más moderno
    
    df = df.copy()
    df['cluster'] = df['cluster'].fillna(-1).astype(int)
    df['cluster_name'] = df['cluster'].map(cluster_names)
    df['cluster_color'] = df['cluster'].map(cluster_colors)
    
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
    
    fig.update_traces(
        textfont=dict(family="Inter"),
        hovertemplate='<b>%{label}</b><br>Dependencia: %{value:.3f}<extra></extra>'
    )
    
    return fig

def display_statistics(viz_data, selected_industry):
    """Estadísticas con diseño mejorado"""
    st.markdown('<div class="stCard">', unsafe_allow_html=True)
    
    cols = st.columns([1, 1, 1])
    
    with cols[0]:
        st.markdown("### 📊 Estadísticas Generales")
        total_dep = viz_data['Value'].sum()
        
        st.markdown(
            f'<div class="metric-card">'
            f'<h4>Dependencia Total</h4>'
            f'<p style="font-size: 24px; font-weight: bold;">{total_dep:.3f}</p>'
            f'</div>',
            unsafe_allow_html=True
        )
        
    with cols[1]:
        st.markdown("### 🔝 Top 5 Dependencias")
        top_5 = viz_data.nlargest(5, 'Value')
        for _, row in top_5.iterrows():
            st.markdown(
                f'<div class="metric-card">'
                f'<p><b>{row["Country"]}</b></p>'
                f'<p>Dependencia: {row["Value"]:.3f}</p>'
                f'</div>',
                unsafe_allow_html=True
            )
            
    with cols[2]:
        st.markdown("### 📈 Distribución por Cluster")
        cluster_stats = viz_data.groupby('cluster_name')['Value'].sum()
        fig = px.pie(
            values=cluster_stats,
            names=cluster_stats.index,
            hole=0.4,
            color=cluster_stats.index,
            color_discrete_map={
                name: color for name, color in zip(
                    cluster_stats.index,
                    px.colors.qualitative.Set3
                )
            }
        )
        fig.update_layout(
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            ),
            margin=dict(t=20, b=20, l=20, r=20)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    # Título principal con estilo mejorado
    st.markdown('<h1 class="main-title">Análisis de Dependencias Comerciales</h1>', unsafe_allow_html=True)
    
    try:
        # Cargar datos
        data = load_dependency_data()
        clustering_data = load_clustering_data()
        
        if data is None or clustering_data is None:
            st.error("⚠️ Error al cargar los datos. Por favor verifica los archivos de entrada.")
            return
        
        # Contenedor para selectores con estilo mejorado
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        cols = st.columns(2)
        
        with cols[0]:
            dependent_countries = sorted(data['dependent_country'].unique())
            default_country_index = dependent_countries.index('ESP') if 'ESP' in dependent_countries else 0
            selected_country = st.selectbox(
                '🌍 País a analizar:',
                dependent_countries,
                index=default_country_index
            )
        
        # ... (resto del código igual pero con mejoras visuales similares)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ... (resto de la implementación)

if __name__ == '__main__':
    main()