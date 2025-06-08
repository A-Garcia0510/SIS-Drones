import streamlit as st
import matplotlib.pyplot as plt
import networkx as nx
from src.model.Graph import Graph
from src.sim.SimulationInitializer import SimulationInitializer
from src.visual.NetworkXAdapter import NetworkXAdapter
from src.visual.AVLVisualizer import AVLVisualizer
from src.tda.AVL import AVL
from src.domain.Route import Route
from src.domain.Order import Order
import pandas as pd
import json

# Must be the first Streamlit command
st.set_page_config(
    page_title="Sistema de Entrega con Drones",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS for dark theme
st.markdown("""
    <style>
    /* Fondo principal */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* Estilo para botones */
    .stButton>button {
        background-color: #262730;
        color: #FAFAFA;
        border: 1px solid #4B4B4B;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        border-color: #6B6B6B;
        background-color: #363840;
    }
    
    /* Estilo para sliders */
    .stSlider>div>div {
        background-color: #262730;
    }
    .stSlider>div>div>div>div {
        background-color: #4B4B4B;
    }
    
    /* Estilo para tabs */
    .stTabs>div>div>div {
        background-color: #262730;
        color: #FAFAFA;
        border-radius: 4px;
    }
    .stTabs>div>div>div:hover {
        background-color: #363840;
    }
    
    /* Estilo para selectbox */
    .stSelectbox>div>div {
        background-color: #262730;
        color: #FAFAFA;
        border: 1px solid #4B4B4B;
    }
    
    /* Estilo para expander */
    .streamlit-expanderHeader {
        background-color: #262730;
        color: #FAFAFA;
    }
    
    /* Estilo para dataframe */
    .stDataFrame {
        background-color: #262730;
    }
    .stDataFrame table {
        background-color: #262730;
    }
    .stDataFrame th {
        background-color: #363840;
        color: #FAFAFA;
    }
    .stDataFrame td {
        color: #FAFAFA;
    }
    
    /* Estilo para métricas */
    .stMetric>div {
        background-color: #262730;
        border: 1px solid #4B4B4B;
        border-radius: 4px;
        padding: 1rem;
    }
    
    /* Estilo para widgets en general */
    .stWidgetLabel {
        color: #FAFAFA !important;
    }
    
    /* Estilo para tooltips */
    .stTooltipIcon {
        color: #FAFAFA;
    }
    
    /* Estilo para markdown */
    .stMarkdown {
        color: #FAFAFA;
    }
    </style>
    """, unsafe_allow_html=True)

# Intentar importar plotly, si no está disponible usar alternativa más simple
try:
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

def run_simulation_tab():
    st.header('⚙️ Inicializar Simulación')
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        num_nodes = st.slider('Número de Nodos', 10, 150, 15, help="Elegir entre 10 y 150 nodos")
        num_edges = st.slider('Número de Aristas', 10, 300, 20, help="Elegir entre 10 y 300 aristas")
        num_orders = st.slider('Número de Órdenes', 1, 500, 14, help="Elegir entre 1 y 500 órdenes")
        st.markdown(f"Nodos Cliente Derivados: {int(num_nodes * 0.6)} ({int(0.6 * 100)}% de {num_nodes})")
    
    with col2:
        if st.button('🚀 Iniciar Simulación', use_container_width=True):
            with st.spinner('Inicializando simulación...'):
                try:
                    # Siempre crear una nueva instancia al iniciar la simulación
                    st.session_state.simulation_initializer = SimulationInitializer()
                    st.session_state.avl_tree = AVL()
                    st.session_state.routes = []
                    st.session_state.route_counter = 0
                    st.session_state.order_counter = 0
                    st.session_state.node_visits = {}
                    st.session_state.orders = []
                    st.session_state.clients = []
                    st.session_state.graph = None
                    st.session_state.network_adapter = None
                    
                    graph, orders, clients = st.session_state.simulation_initializer.initialize_simulation(
                        num_nodes, num_edges, num_orders
                    )
                    
                    if not graph or not graph.vertices():
                        raise ValueError("La inicialización de la red falló")
                    
                    st.session_state.graph = graph
                    st.session_state.orders = orders.copy() if orders else []
                    st.session_state.clients = clients.copy() if clients else []
                    st.session_state.routes = st.session_state.simulation_initializer.routes.copy()
                    st.session_state.order_counter = len(st.session_state.orders)
                    st.session_state.route_counter = len(st.session_state.routes)
                    
                    st.session_state.network_adapter = NetworkXAdapter(st.session_state.graph)
                    st.session_state.network_adapter.convert_to_networkx()
                
                    st.success('✅ Simulación inicializada exitosamente!')
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al inicializar la simulación: {str(e)}")
                    return

def explore_network_tab():
    st.header('🗺️ Explorar Red')
    
    if not st.session_state.graph:
        st.warning('Por favor, ejecute la simulación primero para explorar la red.')
        return
    
    if 'node_visits' not in st.session_state:
        st.session_state.node_visits = {}

    nodes = list(st.session_state.graph.vertices())
    storage_nodes = [n for n in nodes if n.startswith('S')]
    client_nodes = [n for n in nodes if n.startswith('T')]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏁 Nodo Origen")
        origin_type = st.selectbox(
            'Tipo de nodo origen',
            ['Almacenamiento', 'Cliente'],
            key='origin_type'
        )
        
        if origin_type == 'Almacenamiento':
            start_node = st.selectbox('Seleccionar nodo origen', storage_nodes, key='origin')
        else:
            start_node = st.selectbox('Seleccionar nodo origen', client_nodes, key='origin')
    
    with col2:
        st.markdown("#### 🎯 Nodo Destino")
        dest_type = st.selectbox(
            'Tipo de nodo destino',
            ['Cliente', 'Almacenamiento'] if origin_type == 'Almacenamiento' else ['Almacenamiento', 'Cliente'],
            key='dest_type'
        )
        
        if dest_type == 'Almacenamiento':
            end_node = st.selectbox('Seleccionar nodo destino', storage_nodes, key='dest')
        else:
            end_node = st.selectbox('Seleccionar nodo destino', client_nodes, key='dest')

    if 'current_path' not in st.session_state:
        st.session_state.current_path = None
        st.session_state.current_cost = 0
        st.session_state.path_calculated = False

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button('✈️ Calcular Ruta', use_container_width=True):
            st.session_state.network_adapter.clear_path()
            path = st.session_state.simulation_initializer.find_path_with_charging(start_node, end_node)
            
            if path:
                total_cost = 0
                current_autonomy = st.session_state.simulation_initializer.DRONE_AUTONOMY
                valid_path = True
                segments = []
                charging_points = []
                
                for i in range(len(path)-1):
                    edge = st.session_state.graph.get_edge(path[i], path[i+1])
                    if edge:
                        edge_cost = edge.element()
                        if path[i].startswith('C') or path[i+1].startswith('C'):
                            charging_node = path[i] if path[i].startswith('C') else path[i+1]
                            if charging_node not in charging_points:
                                charging_points.append(charging_node)
                            current_autonomy = st.session_state.simulation_initializer.DRONE_AUTONOMY
                            segments.append(f"🔋 Recargando en {charging_node} (Energía restaurada a {current_autonomy})")
                        
                        current_autonomy -= edge_cost
                        segments.append(f"{path[i]} → {path[i+1]} (Costo: {edge_cost}, Energía: {current_autonomy})")
                        
                        if current_autonomy < 0:
                            valid_path = False
                            st.error("❌ No se encontró una ruta viable con la autonomía disponible")
                            st.write("Análisis de ruta:")
                            for segment in segments:
                                st.write(segment)
                            return
                            
                        total_cost += edge_cost
                    else:
                        valid_path = False
                        st.error(f"❌ No hay conexión directa entre {path[i]} y {path[i+1]}")
                        return

                if valid_path:
                    st.session_state.network_adapter.highlight_path(path)
                    st.session_state.current_path = path
                    st.session_state.current_cost = total_cost
                    st.session_state.path_calculated = True
                    
                    with st.expander("📍 Detalles de la Ruta", expanded=True):
                        st.success(f"✅ Ruta encontrada: {' → '.join(path)}")
                        st.info(f"💰 Costo total: {total_cost} unidades")
                        
                        if charging_points:
                            st.warning(f"🔋 La ruta requiere {len(charging_points)} paradas de carga: {', '.join(charging_points)}")
                        
                        st.write("Análisis detallado de la ruta:")
                        for segment in segments:
                            st.write(segment)
            else:
                st.error("❌ No se encontró una ruta viable con la autonomía disponible")
                st.info("💡 El sistema intentará automáticamente rutas a través de estaciones de carga")
                st.session_state.path_calculated = False

    if st.session_state.path_calculated:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button('✅ Completar Entrega y Crear Orden', use_container_width=True):
                try:
                    path = st.session_state.current_path
                    total_cost = st.session_state.current_cost
                    
                    for node in path:
                        if 'node_visits' not in st.session_state:
                            st.session_state.node_visits = {}
                        st.session_state.node_visits[node] = st.session_state.node_visits.get(node, 0) + 1
                    
                    st.session_state.route_counter += 1
                    route_id = f"Ruta_{st.session_state.route_counter}"
                    
                    existing_route = None
                    route_nodes_tuple = tuple(path)
                    
                    for r in st.session_state.routes:
                        if tuple(r.nodes) == route_nodes_tuple:
                            existing_route = r
                            break
                    
                    if existing_route:
                        route = existing_route
                        route.increment_frequency()
                    else:
                        route = Route(route_id, path)
                        route.frequency = 1
                        st.session_state.routes.append(route)
                    
                    st.session_state.order_counter += 1
                    order_id = f"ORD_{st.session_state.order_counter}"
                    
                    client_node = end_node if end_node.startswith('T') else start_node
                    client_num = client_node[1:]
                    client = next((c for c in st.session_state.clients if c.client_id == f"CLI{client_num}"), None)
                    
                    if client:
                        order = Order(
                            order_id=order_id,
                            origin=start_node,
                            destination=end_node,
                            client_id=client.client_id,
                            client_name=client.name,
                            priority=client.client_type
                        )
                        client.add_order(order)
                        
                        order.assign_route(route)
                        order.route_cost = total_cost
                        order.status = "Completado"
                        
                        st.session_state.orders.append(order)
                        
                        st.success("✅ Entrega completada y orden creada exitosamente!")
                        st.session_state.path_calculated = False
                        
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al completar la entrega: {str(e)}")

    st.subheader("🗺️ Visualización de la Red")
    fig = st.session_state.network_adapter.draw_graph()
    st.pyplot(fig)
    plt.close()
    
    st.markdown("""
    ### 🎯 Leyenda
    - 🔵 Nodos de Almacenamiento (S1, S2, ...)
    - 💡 Nodos de Recarga (C1, C2, ...)
    - 🟢 Nodos Cliente (T1, T2, ...)
    - ↔️ Aristas grises: Conexiones disponibles
    - 🔴 Aristas rojas: Ruta seleccionada
    """)

def clients_orders_tab():
    st.header('👥 Clientes y Órdenes')
    
    if not st.session_state.graph:
        st.warning('Por favor, ejecute la simulación primero para ver clientes y órdenes.')
        return
    
    st.subheader('📋 Clientes')
    if st.session_state.clients:
        clients_json = []
        for client in st.session_state.clients:
            total_orders = len([order for order in st.session_state.orders if order.client_id == client.client_id])
            client_data = {
                "ID": client.client_id,
                "Nombre": client.name,
                "Tipo": client.client_type,
                "Total Órdenes": total_orders,
                "Nodo": client.node_id if hasattr(client, 'node_id') else 'N/A'
            }
            clients_json.append(client_data)
        st.json(clients_json)
    else:
        st.info('No hay clientes disponibles.')
    
    st.subheader('📦 Órdenes')
    if st.session_state.orders:
        orders_json = []
        for order in st.session_state.orders:
            if not hasattr(order, 'total_cost') or not order.total_cost:
                total_cost = 0
                if hasattr(order, 'route') and order.route:
                    for i in range(len(order.route.nodes)-1):
                        edge = st.session_state.graph.get_edge(order.route.nodes[i], order.route.nodes[i+1])
                        if edge:
                            total_cost += edge.element()
                    order.total_cost = total_cost
            
            order_data = {
                "ID Orden": order.order_id,
                "ID Cliente": order.client_id if hasattr(order, 'client_id') else None,
                "Nombre Cliente": order.client_name if hasattr(order, 'client_name') else None,
                "Origen": order.origin,
                "Destino": order.destination,
                "Estado": order.status if hasattr(order, 'status') else "Pendiente",
                "Prioridad": order.priority if hasattr(order, 'priority') else "Normal",
                "Fecha Creación": order.creation_date.strftime("%Y-%m-%d %H:%M:%S") if hasattr(order, 'creation_date') and order.creation_date else None,
                "Fecha Entrega": order.delivery_date.strftime("%Y-%m-%d %H:%M:%S") if hasattr(order, 'delivery_date') and order.delivery_date else None,
                "Costo Total": order.total_cost if hasattr(order, 'total_cost') else total_cost,
                "Ruta": ' → '.join(order.route.nodes) if hasattr(order, 'route') and order.route else 'No asignada'
            }
            orders_json.append(order_data)
        st.json(orders_json)
    else:
        st.info('No hay órdenes disponibles.')

def route_analytics_tab():
    st.header('📋 Análisis de Rutas')
    
    if not st.session_state.routes:
        st.info('No hay rutas registradas aún. Use la pestaña "Explorar Red" para crear rutas.')
        return

    try:
        sorted_routes = sorted(st.session_state.routes, key=lambda x: x.frequency, reverse=True)

        avl_tree = AVL()
        for route in sorted_routes:
            avl_tree.insert(route)
        
        st.subheader('🌳 Árbol AVL de Frecuencias de Rutas')
        avl_visualizer = AVLVisualizer(avl_tree)
        fig = avl_visualizer.visualize()
        st.pyplot(fig)
        plt.close()

        st.subheader('🔄 Rutas Más Frecuentes')
        routes_data = []
        for route in sorted_routes:
            routes_data.append({
                'Ruta': ' → '.join(route.nodes),
                'Frecuencia': route.frequency,
                'Nodos': len(route.nodes),
                'Origen': route.nodes[0],
                'Destino': route.nodes[-1]
            })
        
        df_routes = pd.DataFrame(routes_data)
        st.dataframe(
            df_routes,
            column_config={
                "Ruta": "Secuencia de Nodos",
                "Frecuencia": st.column_config.NumberColumn("Frecuencia de Uso", format="%d"),
                "Nodos": "Cantidad de Nodos",
                "Origen": "Nodo Origen",
                "Destino": "Nodo Destino"
            },
            hide_index=True
        )

        st.subheader('📈 Estadísticas de Rutas')
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_routes = len(st.session_state.routes)
            st.metric("Total de Rutas Únicas", total_routes)
        
        with col2:
            total_frequency = sum(route.frequency for route in st.session_state.routes)
            st.metric("Total de Viajes Realizados", total_frequency)
        
        with col3:
            avg_frequency = total_frequency / total_routes if total_routes > 0 else 0
            st.metric("Promedio de Uso por Ruta", f"{avg_frequency:.2f}")
    except Exception as e:
        st.error(f"Error al procesar las rutas: {str(e)}")
        return

def general_statistics_tab():
    st.header('📈 Estadísticas Generales')
    
    if not st.session_state.graph:
        st.warning('Por favor, ejecute la simulación primero para ver las estadísticas.')
        return
    
    # Título para la sección de nodos más visitados
    st.subheader('📊 Nodos Más Visitados por Rol')
    
    # Obtener y filtrar nodos por tipo
    nodes = list(st.session_state.graph.vertices())
    storage_nodes = [n for n in nodes if n.startswith('S')]
    charging_nodes = [n for n in nodes if n.startswith('C')]
    client_nodes = [n for n in nodes if n.startswith('T')]
    
    # Crear tres columnas para los gráficos
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("👥 Clientes Más Visitados")
        client_visits = {node: st.session_state.node_visits.get(node, 0) 
                        for node in nodes 
                        if node.startswith('T')}
        if client_visits:
            df_clients = pd.DataFrame({
                'Node': list(client_visits.keys()),
                'Visits': list(client_visits.values())
            }).sort_values('Visits', ascending=False)
            
            fig = plt.figure(figsize=(8, 5))
            plt.bar(df_clients['Node'], df_clients['Visits'], color='#66B2FF')
            plt.xticks(rotation=45)
            plt.title('Visitas a Nodos Cliente')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

    with col2:
        st.markdown("🔋 Estaciones de Recarga Más Visitadas")
        charging_visits = {node: st.session_state.node_visits.get(node, 0) 
                         for node in nodes 
                         if node.startswith('C')}
        if charging_visits:
            df_charging = pd.DataFrame({
                'Node': list(charging_visits.keys()),
                'Visits': list(charging_visits.values())
            }).sort_values('Visits', ascending=False)
            
            fig = plt.figure(figsize=(8, 5))
            plt.bar(df_charging['Node'], df_charging['Visits'], color='#66B2FF')
            plt.xticks(rotation=45)
            plt.title('Visitas a Estaciones de Recarga')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

    with col3:
        st.markdown("📦 Almacenes Más Visitados")
        storage_visits = {node: st.session_state.node_visits.get(node, 0) 
                        for node in nodes 
                        if node.startswith('S')}
        if storage_visits:
            df_storage = pd.DataFrame({
                'Node': list(storage_visits.keys()),
                'Visits': list(storage_visits.values())
            }).sort_values('Visits', ascending=False)
            
            fig = plt.figure(figsize=(8, 5))
            plt.bar(df_storage['Node'], df_storage['Visits'], color='#66B2FF')
            plt.xticks(rotation=45)
            plt.title('Visitas a Nodos de Almacenamiento')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

    # Distribución de roles de nodos
    st.subheader('🔄 Gráfico de Torta: Distribución de Roles de Nodos')
    
    # Contar nodos por tipo
    node_types = {
        "Almacenamiento": len(storage_nodes),
        "Recarga": len(charging_nodes),
        "Cliente": len(client_nodes)
    }
    
    fig = plt.figure(figsize=(10, 6))
    plt.pie(
        list(node_types.values()),
        labels=list(node_types.keys()),
        colors=['#FF9999', '#66B2FF', '#99FF99'],
        autopct='%1.1f%%',
        startangle=90
    )
    plt.title('Distribución de Nodos por Rol')
    st.pyplot(fig)
    plt.close()
    
    # Estadísticas adicionales en columnas
    st.subheader('📊 Estadísticas Adicionales')
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total de Nodos", len(nodes))
        st.metric("Nodos de Almacenamiento", len(storage_nodes))
    
    with col2:
        st.metric("Nodos de Recarga", len(charging_nodes))
        st.metric("Nodos Cliente", len(client_nodes))
    
    with col3:
        total_edges = sum(1 for _ in st.session_state.graph.edges())
        st.metric("Total de Conexiones", total_edges)
        avg_connections = total_edges / len(nodes) if len(nodes) > 0 else 0
        st.metric("Promedio de Conexiones", f"{avg_connections:.2f}")
    
    # Estadísticas de órdenes
    st.subheader('📦 Estadísticas de Órdenes')
    if st.session_state.orders:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_orders = len(st.session_state.orders)
            st.metric('Total de Órdenes', total_orders)
        
        with col2:
            avg_cost = sum(order.route_cost for order in st.session_state.orders) / total_orders if total_orders > 0 else 0
            st.metric('Costo Promedio', f"{avg_cost:.2f}")
        
        with col3:
            priorities = [order.priority for order in st.session_state.orders]
            most_common = max(set(priorities), key=priorities.count) if priorities else "N/A"
            st.metric('Prioridad Más Común', most_common)
    else:
        st.info('No hay datos de órdenes disponibles.')

def tabs_container():
    tabs = st.tabs([
        "⚙️ Inicializar Simulación",
        "🗺️ Explorar Red",
        "👥 Clientes y Órdenes",
        "📋 Análisis de Rutas",
        "📈 Estadísticas"
    ])
    
    with tabs[0]:
        run_simulation_tab()
    with tabs[1]:
        explore_network_tab()
    with tabs[2]:
        clients_orders_tab()
    with tabs[3]:
        route_analytics_tab()
    with tabs[4]:
        general_statistics_tab()

def run_dashboard():
    # Main title
    st.title('🚁 Sistema de Entrega con Drones')
    
    # Initialize session state variables if they don't exist
    if 'graph' not in st.session_state:
        st.session_state.graph = None
    if 'simulation_initializer' not in st.session_state:
        st.session_state.simulation_initializer = None
    if 'network_adapter' not in st.session_state:
        st.session_state.network_adapter = None
    if 'routes' not in st.session_state:
        st.session_state.routes = []
    if 'orders' not in st.session_state:
        st.session_state.orders = []
    if 'clients' not in st.session_state:
        st.session_state.clients = []
    if 'route_counter' not in st.session_state:
        st.session_state.route_counter = 0
    if 'order_counter' not in st.session_state:
        st.session_state.order_counter = 0
    
    # Show tabs
    tabs_container()

if __name__ == "__main__":
    run_dashboard() 