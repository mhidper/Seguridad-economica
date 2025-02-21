import pandas as pd
from pathlib import Path
import gzip

# Obtener la ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent

def load_dependency_data(filename="dependencias.csv.gz"):
    """
    Carga el CSV consolidado de dependencias desde un archivo comprimido.
    
    Args:
        filename (str): Nombre del archivo comprimido
        
    Returns:
        pd.DataFrame: DataFrame con los datos de dependencias
    """
    csv_path = BASE_DIR / "src" / "data" / "processed" / "Dependencias consolidadas" / filename
    
    try:
        with gzip.open(csv_path, 'rt') as file:
            return pd.read_csv(file, sep=";")
    except Exception as e:
        print(f"Error al cargar el archivo de dependencias: {e}")
        return None

def load_clustering_data(filename="agglomerative_clustering_results.csv"):
    """
    Carga los datos de clustering.
    
    Args:
        filename (str): Nombre del archivo de clustering
        
    Returns:
        pd.DataFrame: DataFrame con los resultados del clustering
    """
    clustering_path = BASE_DIR / "src" / "data" / "processed" / "comunidades" / filename
    
    try:
        return pd.read_csv(clustering_path, sep=';')
    except Exception as e:
        print(f"Error al cargar el archivo de clustering: {e}")
        return None

def build_dependency_matrix(data, target_country):
    """
    Construye la matriz de dependencia para un país objetivo desde el CSV consolidado.
    
    Args:
        data (pd.DataFrame): DataFrame con los datos de dependencias
        target_country (str): País objetivo para construir la matriz
        
    Returns:
        pd.DataFrame: Matriz de dependencia para el país objetivo
    """
    if data is None:
        return None
        
    try:
        country_data = data[data['dependent_country'] == target_country]
        matrix = country_data.pivot(
            index='industry',
            columns='supplier_country',
            values='dependency_value'
        ).fillna(0)
        return matrix
    except Exception as e:
        print(f"Error al construir la matriz de dependencia: {e}")
        return None

def process_data_for_visualization(df, clustering_data, selected_industry=None):
    """
    Procesa el DataFrame para visualización, incluyendo información de clusters.
    
    Args:
        df (pd.DataFrame): DataFrame con la matriz de dependencia
        clustering_data (pd.DataFrame): DataFrame con la información de clusters
        selected_industry (str, optional): Industria seleccionada para filtrar
        
    Returns:
        pd.DataFrame: DataFrame procesado para visualización
    """
    if df is None or clustering_data is None:
        return None
        
    try:
        if selected_industry and selected_industry != 'Todas las industrias':
            # Procesar datos para una industria específica
            industry_data = df.loc[selected_industry]
            significant_countries = industry_data[industry_data > 0].sort_values(ascending=False)
            
            viz_data = pd.DataFrame({
                'Industry': selected_industry,
                'Country': significant_countries.index,
                'Value': significant_countries.values
            })
        else:
            # Procesar datos para todas las industrias
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
        
        # Merge con los datos de clustering
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
        
    except Exception as e:
        print(f"Error al procesar datos para visualización: {e}")
        return None