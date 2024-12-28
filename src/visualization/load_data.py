import pandas as pd
from pathlib import Path

# Obtener la ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent

def load_dependency_data(filename="dependencias_consolidadas.csv"):
    """
    Carga el CSV consolidado de dependencias.
    """
    csv_path = BASE_DIR / "src" / "data" / "processed" / "Dependencias consolidadas" / filename
    return pd.read_csv(csv_path)

def load_clustering_data(filename="agglomerative_clustering_results.csv"):
    """
    Carga los datos de clustering.
    """
    clustering_path = BASE_DIR / "src" / "data" / "processed" / "comunidades" / filename
    return pd.read_csv(clustering_path, sep=';')

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
        
        viz_data = pd.DataFrame({
            'Industry': selected_industry,
            'Country': significant_countries.index,
            'Value': significant_countries.values
        })
        
        # Ajustar el merge para usar la columna correcta
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
        
        viz_data = pd.merge(
            viz_data,
            clustering_data[['iso_d', 'cluster']],
            left_on='Country',
            right_on='iso_d',
            how='left'
        )
    
    viz_data = viz_data.sort_values(['cluster', 'Value'], ascending=[True, False])
    
    return viz_data