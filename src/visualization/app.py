import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from pathlib import Path
import gzip
from load_data_new import load_dependency_data, load_clustering_data, build_dependency_matrix, process_data_for_visualization

# Configuración de la página para usar todo el ancho
st.set_page_config(
    page_title="Análisis de Dependencias Comerciales",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado para eliminar padding y centrar contenido
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        .element-container {
            width: 100%;
        }
        [data-testid="stSidebar"] {
            display: none;
        }
        .stApp {
            margin: auto;
        }
    </style>
""", unsafe_allow_html=True)

def get_cluster_colors():
    """
    Define los colores para cada cluster basados en el nivel de riesgo
    Rojo -> Naranja -> Amarillo -> Verde claro -> Verde
    """
    cluster_colors = {
        1: '#FF4444',  # Rojo para "Estados con Desafíos Geopolíticos"
        0: '#FFA500',  # Naranja para "Economías Emergentes y en Desarrollo"
        4: '#FFD700',  # Amarillo para "América Latina: Aliados Regionales Clave"
        2: '#90EE90',  # Verde oscuro para "Socios Históricos y Culturales"
        3: '#228B22'   # Verde claro para "Economías Avanzadas y Aliados Estratégicos"
    }
    return cluster_colors

def create_treemap(df, country):
    """
    Crea el treemap usando plotly con colores basados en nivel de riesgo
    """
    cluster_names = {
        0: "Economías Emergentes y en Desarrollo",
        1: "Estados con Desafíos Geopolíticos",
        2: "Economías Avanzadas y Aliados Estratégicos",
        3: "Socios Históricos y Culturales",
        4: "América Latina: Aliados Regionales Clave",
        -1: "Cluster No Asignado"  # Para países sin cluster asignado
    }
    
    # Obtener los colores
    cluster_colors = get_cluster_colors()
    cluster_colors[-1] = '#808080'  # Gris para cluster no asignado
    
    # Asegurarse de que no hay valores nulos
    df = df.copy()
    df['cluster'] = df['cluster'].fillna(-1).astype(int)
    df['cluster_name'] = df['cluster'].map(cluster_names)
    df['cluster_name'] = df['cluster_name'].fillna("Cluster No Asignado")
    df['cluster_color'] = df['cluster'].map(cluster_colors)
    
    # Crear una columna combinada para el path
    df['Country_Cluster'] = df['Country'] + ' (' + df['cluster_name'] + ')'
    
    # Asegurarse de que todos los valores numéricos son válidos
    df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
    df = df.dropna(subset=['Value'])
    
    if df.empty:
        raise ValueError("No hay datos válidos para crear el treemap")
    
    fig = px.treemap(
        df,
        path=['Industry', 'cluster_name', 'Country'],
        values='Value',
        title=f'Dependencias de {country} por Industria y País',
        color='cluster_name',
        color_discrete_map={name: cluster_colors[num] for num, name in cluster_names.items()}
    )
    
    fig.update_traces(
        textinfo="label+value",
        texttemplate="<b>%{label}</b><br>%{value:.3f}",
        hovertemplate='<b>%{label}</b><br>Dependencia: %{value:.3f}<extra></extra>'
    )
    
    fig.update_layout(
        width=None,
        height=800,
        title={
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        showlegend=True,
        coloraxis_showscale=False,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255, 255, 255, 0.8)"
        )
    )
    
    return fig

def create_choropleth_map(viz_data, country, selected_industry):
    """
    Crea un mapa choropleth usando los códigos ISO3 de los países.
    """
    if selected_industry != 'Todas las industrias':
        map_data = viz_data[['Country', 'Value']].copy()
        title = f'Dependencias de {country} en {selected_industry}'
    else:
        map_data = viz_data.groupby('Country')['Value'].mean().reset_index()
        title = f'Dependencias promedio de {country} por país'
    
    fig = px.choropleth(
        map_data,
        locations='Country',
        color='Value',
        hover_name='Country',
        color_continuous_scale='RdBu_r',
        title=title
    )
    
    fig.update_layout(
        title={
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular'
        ),
        width=None,
        height=600,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    return fig

def display_statistics(viz_data, selected_industry, selected_country, data):
    """
    Muestra estadísticas consistentes con el treemap y añade análisis por cluster.
    Incluye una nueva columna para mostrar los principales países proveedores.
    """
    cluster_names = {
        0: "Economías Emergentes y en Desarrollo",
        1: "Estados con Desafíos Geopolíticos",
        2: "Economías Avanzadas y Aliados Estratégicos",
        3: "Socios Históricos y Culturales",
        4: "América Latina: Aliados Regionales Clave"
    }
    
    cluster_colors = get_cluster_colors()
    viz_data['cluster_name'] = viz_data['cluster'].map(cluster_names)
    
    # Crear tres columnas
    col1, col2, col3 = st.columns([1, 1, 1])

    # Columna 1: Estadísticas de Dependencia
    with col1:
        st.subheader('Estadísticas de Dependencia')
        if selected_industry != 'Todas las industrias':
            total_dependency = viz_data['Value'].sum()
            st.metric(f'Dependencia Total para {selected_industry}', f'{total_dependency:.3f}')
            
            cluster_stats = viz_data.groupby('cluster_name')['Value'].agg(['sum', 'count']).round(3)
            cluster_stats['percentage'] = (cluster_stats['sum'] / total_dependency * 100).round(2)
            cluster_stats = cluster_stats.sort_values('sum', ascending=False)
            
            st.write("Dependencia por Cluster:")
            for idx, row in cluster_stats.iterrows():
                st.write(f"**{idx}**")
                st.write(f"- Suma: {row['sum']:.3f}")
                st.write(f"- Porcentaje: {row['percentage']:.2f}%")
                st.write(f"- Número de países: {row['count']}")
    
    # Columna 2: Principales Dependencias
    with col2:
        if selected_industry != 'Todas las industrias':
            st.subheader(f'Principales Dependencias en {selected_industry}')
            top_deps = viz_data.nlargest(10, 'Value')
            top_df = pd.DataFrame({
                'País': top_deps['Country'],
                'Cluster': top_deps['cluster_name'],
                'Dependencia': top_deps['Value'].round(3)
            })
            st.dataframe(top_df, width=None)
        else:
            st.subheader('Top 10 Dependencias más Altas')
            top_10 = viz_data.nlargest(10, 'Value')
            st.dataframe(
                top_10[['Industry', 'Country', 'cluster_name', 'Value']].round(3),
                width=None
            )
    
    # Columna 3: Principales Países Proveedores
    with col3:
        st.subheader(f'Principales Proveedores de {selected_country}')
        
        # Calcular las dependencias ponderadas
        def safe_weighted_average(group):
            if group['trade_value'].sum() == 0:
                return np.nan
            return np.average(group['dependency_value'], weights=group['trade_value'])
        
        weighted_dependencies = data.groupby(['dependent_country', 'supplier_country']).apply(
            safe_weighted_average
        ).reset_index(name='weighted_dependency')
        
        # Filtrar para el país seleccionado
        country_dependencies = weighted_dependencies[weighted_dependencies['dependent_country'] == selected_country]
        country_dependencies = country_dependencies.dropna().sort_values('weighted_dependency', ascending=False)
        
        # Mostrar los principales proveedores
        if not country_dependencies.empty:
            st.write("Principales países proveedores:")
            st.dataframe(
                country_dependencies[['supplier_country', 'weighted_dependency']].head(10),
                width=None,
                column_config={
                    'supplier_country': 'País Proveedor',
                    'weighted_dependency': 'Dependencia Ponderada'
                }
            )
        else:
            st.write("No hay datos de proveedores para este país.")

def main():
    st.title('Análisis de Dependencias Comerciales')
    
    try:
        # Cargar datos
        data = load_dependency_data()
        clustering_data = load_clustering_data()
        
        if data is None or clustering_data is None:
            st.error("Error al cargar los datos. Por favor verifica los archivos de entrada.")
            return
            
        # Contenedor para los selectores
        col1, col2 = st.columns(2)
        
        with col1:
            dependent_countries = sorted(data['dependent_country'].unique())
            default_country_index = dependent_countries.index('ESP') if 'ESP' in dependent_countries else 0
            selected_country = st.selectbox(
                'Seleccione un país para analizar sus dependencias:',
                dependent_countries,
                index=default_country_index
            )
        
        if selected_country:
            dependency_matrix = build_dependency_matrix(data, selected_country)
            
            if dependency_matrix is None or dependency_matrix.empty:
                st.error(f"No hay datos disponibles para {selected_country}")
                return
                
            with col2:
                industries = ['Todas las industrias'] + list(dependency_matrix.index)
                selected_industry = st.selectbox(
                    'Seleccione una industria:',
                    industries,
                    index=0
                )
            
            # Procesar datos y mostrar visualizaciones
            viz_data = process_data_for_visualization(dependency_matrix, clustering_data, selected_industry)
            
            if viz_data is None or viz_data.empty:
                st.error(f"No hay datos de dependencias para mostrar con la selección actual")
                return
            
            if not viz_data['Value'].isnull().all():
                tab1, tab2 = st.tabs(["Mapa Mundial", "Árbol de Dependencias"])
                
                with tab1:
                    try:
                        map_fig = create_choropleth_map(viz_data, selected_country, selected_industry)
                        st.plotly_chart(map_fig, use_container_width=True)
                    except Exception as e:
                        st.error(f"Error al crear el mapa: {str(e)}")
                        
                with tab2:
                    try:
                        viz_data['cluster'] = viz_data['cluster'].fillna(-1)
                        tree_fig = create_treemap(viz_data, selected_country)
                        st.plotly_chart(tree_fig, use_container_width=True)
                    except Exception as e:
                        st.error(f"Error al crear el árbol de dependencias: {str(e)}")
                
                try:
                    # Pasar el parámetro `data` a la función
                    display_statistics(viz_data, selected_industry, selected_country, data)
                except Exception as e:
                    st.error(f"Error al mostrar las estadísticas: {str(e)}")
            else:
                st.warning("No hay datos válidos para mostrar con la selección actual")
                
    except Exception as e:
        st.error(f"Error inesperado: {str(e)}")

if __name__ == '__main__':
    main()