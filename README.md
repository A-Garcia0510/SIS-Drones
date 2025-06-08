# 🚁 Sistema de Entrega con Drones

## 📦 Descripción
Sistema logístico autónomo que simula y optimiza la entrega de paquetes utilizando drones. El sistema gestiona una red de nodos que incluye centros de almacenamiento, estaciones de recarga y puntos de entrega a clientes.

## ✨ Características Principales

### 🎯 Gestión de Red
- Hasta 150 nodos en la red
- Distribución automática de roles:
  * 📦 20% Almacenamiento
  * 🔋 20% Recarga
  * 👤 60% Clientes
- Autonomía máxima de 50 unidades por dron
- Recarga automática en estaciones

### 🛣️ Sistema de Rutas
- Cálculo dinámico de rutas óptimas
- Consideración automática de puntos de recarga
- Algoritmos implementados: BFS, DFS, Ordenamiento Topológico
- Registro y análisis de frecuencias de uso

### 📊 Visualización y Análisis
- Dashboard interactivo con 5 pestañas:
  1. 🔄 Ejecutar Simulación
  2. 🌍 Explorar Red
  3. 👥 Clientes y Órdenes
  4. 📋 Análisis de Rutas
  5. 📈 Estadísticas Generales

## 🛠️ Tecnologías Utilizadas
- Python 3.8+
- Streamlit (interfaz gráfica)
- NetworkX (visualización de grafos)
- Matplotlib (gráficos estadísticos)
- Pandas (manejo de datos)

## 📋 Requisitos del Sistema
- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Conexión a Internet (para descargar dependencias)

## 🚀 Instalación

1. Clonar el repositorio:
```bash
git clone [URL_DEL_REPOSITORIO]
cd SIS-Drones
```

2. Crear y activar entorno virtual (opcional pero recomendado):
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## 💻 Uso

1. Iniciar la aplicación:
```bash
streamlit run src/app.py
```

2. Acceder a través del navegador:
```
http://localhost:8501
```

## 📱 Guía de Uso

### 1. Pestaña de Simulación
- Ajustar número de nodos (10-150)
- Configurar cantidad de aristas
- Establecer número de órdenes
- Iniciar simulación

### 2. Explorar Red
- Seleccionar nodos de origen y destino
- Calcular rutas óptimas
- Visualizar caminos en el grafo
- Crear órdenes de entrega

### 3. Gestión de Órdenes
- Ver órdenes activas
- Monitorear estado de entregas
- Consultar detalles de clientes

### 4. Análisis de Rutas
- Visualizar rutas más frecuentes
- Analizar patrones de uso
- Consultar estadísticas de eficiencia

### 5. Estadísticas
- Ver distribución de nodos
- Analizar métricas de uso
- Consultar rendimiento general

## 🤝 Contribuir
¿Encontraste un bug o tienes una sugerencia? ¡Nos encantaría escucharte!
1. Haz fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia
Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE.md](LICENSE.md) para más detalles.

## ✨ Autores
- [Tu Nombre] - *Desarrollo Inicial* - [Tu Usuario de GitHub]

## 🙏 Agradecimientos
- Profesor de INFO1126 - Programación 3
- Compañeros de curso por el feedback
- Comunidad de desarrollo por las librerías utilizadas