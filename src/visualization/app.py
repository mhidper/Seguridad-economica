import streamlit as st
import pandas as pd
import plotly.express as px

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

def load_dependency_data(csv_path):
    """
    Carga el CSV consolidado de dependencias.
    """
    return pd.read_csv(csv_path)

def build_dependency_matrix(data, target_country):
    """
    Construye la matriz de dependencia para un país objetivo desde el CSV consolidado.
    """
    country_data = data[data['dependent_country'] == target_country]
    matrix = country_data.pivot(
        index='industry',
        columns='supplier_country',
        values='dependency_value'
    ).fillna(0)
    return matrix

def process_data_for_visualization(df, clustering_data, selected_industry=None):
    """
    Procesa el DataFrame para visualización, incluyendo información de clusters
    """
    if selected_industry and selected_industry != 'Todas las industrias':
        industry_data = df.loc[selected_industry]
        significant_countries = industry_data[industry_data > 0].sort_values(ascending=False)
        
        # Crear DataFrame base
        viz_data = pd.DataFrame({
            'Industry': selected_industry,
            'Country': significant_countries.index,
            'Value': significant_countries.values
        })
        
        # Añadir información del cluster
        viz_data = pd.merge(
            viz_data,
            clustering_data[['iso_d', 'cluster']],
            left_on='Country',
            right_on='iso_d',
            how='left'
        )
    else:
        viz_data = []
        for industry in df.index:
            industry_data = df.loc[industry]
            significant_countries = industry_data[industry_data > 0].sort_values(ascending=False)
            for country, value in significant_countries.items():
                viz_data.append({
                    'Industry': industry,
                    'Country': country,
                    'Value': value
                })
        viz_data = pd.DataFrame(viz_data)
        
        # Añadir información del cluster
        viz_data = pd.merge(
            viz_data,
            clustering_data[['iso_d', 'cluster']],
            left_on='Country',
            right_on='iso_d',
            how='left'
        )
    
    # Ordenar por cluster y valor
    viz_data = viz_data.sort_values(['cluster', 'Value'], ascending=[True, False])
    
    return viz_data

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
        4: "América Latina: Aliados Regionales Clave"
    }
    
    # Obtener los colores
    cluster_colors = get_cluster_colors()
    
    # Crear una nueva columna con los nombres descriptivos de los clusters
    df['cluster_name'] = df['cluster'].map(cluster_names)
    df['cluster_color'] = df['cluster'].map(cluster_colors)
    
    # Crear una columna combinada para el path
    df['Country_Cluster'] = df['Country'] + ' (' + df['cluster_name'] + ')'
    
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
        coloraxis_showscale=False
    )
    
    # Ajustar la posición de la leyenda
    fig.update_layout(
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

def display_statistics(viz_data, selected_industry):
    """
    Muestra estadísticas consistentes con el treemap y añade análisis por cluster.
    """
    cluster_names = {
        0: "Economías Emergentes y en Desarrollo",
        1: "Estados con Desafíos Geopolíticos",
        2: "Economías Avanzadas y Aliados Estratégicos",
        3: "Socios Históricos y Culturales",
        4: "América Latina: Aliados Regionales Clave"
    }
    
    # Obtener los colores
    cluster_colors = get_cluster_colors()
    
    # Añadir nombres descriptivos de clusters
    viz_data['cluster_name'] = viz_data['cluster'].map(cluster_names)
    
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.subheader('Estadísticas de Dependencia')
        if selected_industry != 'Todas las industrias':
            total_dependency = viz_data['Value'].sum()
            st.metric(f'Dependencia Total para {selected_industry}', f'{total_dependency:.3f}')
            
            # Calcular estadísticas por cluster
            cluster_stats = viz_data.groupby('cluster_name')['Value'].agg(['sum', 'count']).round(3)
            cluster_stats['percentage'] = (cluster_stats['sum'] / total_dependency * 100).round(2)
            cluster_stats = cluster_stats.sort_values('sum', ascending=False)
            
            st.write("Dependencia por Cluster:")
            for idx, row in cluster_stats.iterrows():
                st.write(f"**{idx}**")
                st.write(f"- Suma: {row['sum']:.3f}")
                st.write(f"- Porcentaje: {row['percentage']:.2f}%")
                st.write(f"- Número de países: {row['count']}")
    
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
    
    with col3:
        if selected_industry != 'Todas las industrias':
            st.subheader('Distribución por Cluster')
            
            # Calcular estadísticas por cluster para el gráfico de tarta
            cluster_stats = viz_data.groupby('cluster_name')['Value'].sum().round(3)
            
            # Crear gráfico de tarta con los colores específicos
            fig = px.pie(
                values=cluster_stats,
                names=cluster_stats.index,
                title='Distribución de Dependencia por Cluster',
                color=cluster_stats.index,
                color_discrete_map={name: cluster_colors[num] for num, name in cluster_names.items()}
            )
            
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate="<b>%{label}</b><br>" +
                            "Dependencia: %{value:.3f}<br>" +
                            "Porcentaje: %{percent}<br>" +
                            "<extra></extra>"
            )
            
            fig.update_layout(
                showlegend=False,
                height=400,
                margin=dict(t=30, b=0, l=0, r=0)
            )
            
            st.plotly_chart(fig, use_container_width=True)

def main():
    st.title('Análisis de Dependencias Comerciales')
    
    # Cargar datos
    csv_path = "C:/Users/Usuario/Documents/Github/Seguridad económica/Resultados/CSV dependencia/dependencias_consolidadas.csv"
    clustering_path = "C:/Users/Usuario/Documents/Github/Seguridad económica/Resultados/comunidades/agglomerative_clustering_results.csv"
    
    data = load_dependency_data(csv_path)
    clustering_data = pd.read_csv(clustering_path, sep=';')
    
    # Contenedor para los selectores
    col1, col2 = st.columns(2)
    
    with col1:
        dependent_countries = sorted(data['dependent_country'].unique())
        selected_country = st.selectbox(
            'Seleccione un país para analizar sus dependencias:',
            dependent_countries
        )
    
    if selected_country:
        dependency_matrix = build_dependency_matrix(data, selected_country)
        
        with col2:
            industries = ['Todas las industrias'] + list(dependency_matrix.index)
            selected_industry = st.selectbox(
                'Seleccione una industria:',
                industries
            )
        
        # Procesar datos y mostrar visualizaciones
        viz_data = process_data_for_visualization(dependency_matrix, clustering_data, selected_industry)
        
        # Crear pestañas para las diferentes visualizaciones
        tab1, tab2 = st.tabs(["Mapa Mundial", "Árbol de Dependencias"])
        
        with tab1:
            map_fig = create_choropleth_map(viz_data, selected_country, selected_industry)
            st.plotly_chart(map_fig, use_container_width=True)
            
        with tab2:
            tree_fig = create_treemap(viz_data, selected_country)
            st.plotly_chart(tree_fig, use_container_width=True)
        
        # Mostrar estadísticas
        display_statistics(viz_data, selected_industry)

if __name__ == '__main__':
    main()