import streamlit as st
import osmnx as ox
import networkx as nx
import folium
from streamlit_folium import folium_static

# Cache the graph loading
@st.cache_data
def load_dehradun_graph():
    try:
        G = ox.graph_from_place("Dehradun, Uttarakhand, India", network_type="drive")
        # Convert to simple directed graph to avoid multigraph issues
        G_simple = nx.DiGraph(G)
        return G_simple
    except Exception as e:
        st.error(f"Error loading map data: {e}")
        return None

# Calculate shortest route by distance
def get_shortest_route(G, origin_node, destination_node):
    try:
        route = nx.shortest_path(G, origin_node, destination_node, weight='length')
        return route
    except nx.NetworkXNoPath:
        st.error("No path exists between these locations.")
        return None

# Calculate route length in km
def get_route_length_km(G, route):
    length = 0
    for i in range(len(route) - 1):
        edge_data = G.get_edge_data(route[i], route[i+1], 0)
        length += edge_data.get('length', 0)
    return length / 1000

# Create folium map showing the route
def create_route_map(G, route, start_name, end_name):
    route_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in route]
    center_lat = sum([pt[0] for pt in route_coords]) / len(route_coords)
    center_lon = sum([pt[1] for pt in route_coords]) / len(route_coords)

    route_map = folium.Map(location=[center_lat, center_lon], zoom_start=13)
    
    folium.PolyLine(route_coords, color='blue', weight=6, opacity=0.7).add_to(route_map)

    # Add start and end markers
    folium.Marker(route_coords[0], popup=f"Start: {start_name}", icon=folium.Icon(color='green')).add_to(route_map)
    folium.Marker(route_coords[-1], popup=f"End: {end_name}", icon=folium.Icon(color='red')).add_to(route_map)

    return route_map

# Predefined popular locations in Dehradun
@st.cache_data
def get_locations():
    return {
        "Clock Tower": (30.3253, 78.0413),
        "ISBT": (30.2881, 78.0428),
        "Rajpur Road": (30.3440, 78.0689),
        "Pacific Mall": (30.3387, 78.0554),
        "Forest Research Institute": (30.3417, 77.9996),
        "Robber's Cave": (30.3752, 78.0689),
        "Sahastradhara": (30.3879, 78.1231),
        "Mussoorie Road": (30.4059, 78.0300),
        "Buddha Temple": (30.3358, 78.0433),
        "Paltan Bazaar": (30.3218, 78.0440)
    }

def main():
    st.title("🚗 Dehradun Shortest Route Finder")

    G = load_dehradun_graph()
    if G is None:
        st.stop()

    locations = get_locations()
    location_names = list(locations.keys())

    start_location = st.selectbox("Select start location:", location_names)
    end_location = st.selectbox("Select destination:", location_names, index=1)

    if start_location == end_location:
        st.warning("Start and destination must be different.")
        st.stop()

    if st.button("Find Shortest Route"):
        start_coords = locations[start_location]
        end_coords = locations[end_location]

        origin_node = ox.distance.nearest_nodes(G, start_coords[1], start_coords[0])
        destination_node = ox.distance.nearest_nodes(G, end_coords[1], end_coords[0])

        route = get_shortest_route(G, origin_node, destination_node)
        if route is None:
            st.error("No route found.")
            st.stop()

        distance_km = get_route_length_km(G, route)

        route_map = create_route_map(G, route, start_location, end_location)
        st.subheader(f"Shortest Route from {start_location} to {end_location}")
        folium_static(route_map, width=800, height=500)
        st.markdown(f"**Distance:** {distance_km:.2f} km")

if __name__ == "__main__":
    main()
