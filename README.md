 # indice_seguridad
Indicador de seguridad para RIELCANO


# Índice de Seguridad Económica

Este proyecto desarrolla un índice de seguridad económica basado en el análisis de dependencias comerciales internacionales para el Real Instituto Elcano.

## Descripción

El análisis se fundamenta en datos de comercio internacional y está diseñado para proporcionar una medida objetiva de la seguridad económica a través del estudio de las dependencias comerciales entre naciones.

## Estructura del Proyecto

seguridad_economica/
├── src/                      # Código fuente
│   ├── data/                # Procesamiento de datos
│   │   └── load_data.py
│   └── visualization/       # Visualización
│       └── dependency_dashboard.py
├── data/                    # Datos
│   ├── raw/                # Datos sin procesar
│   │   └── ITP/           # Datos ITP originales
│   └── processed/         # Datos procesados
├── docs/                   # Documentación
│   ├── metodologia/
│   └── images/
└── requirements.txt        # Dependencias del proyecto

## Instalación

1. Clonar el repositorio
```bash
git clone [URL del repositorio]
cd seguridad_economica

Instalar dependencias
pip install -r requirements.txt
Uso
Para ejecutar la aplicación de visualización:
bashCopystreamlit run src/visualization/dependency_dashboard.py
La aplicación permite:

Visualizar dependencias comerciales por país
Analizar patrones por industria
Ver distribuciones por clusters de países
Explorar datos a través de mapas y visualizaciones interactivas

Metodología
[Aquí podríamos añadir una breve descripción de la metodología o un enlace al documento metodológico]
Autores

[Tu nombre/organización]
Real Instituto Elcano

Licencia
[Tipo de licencia]
