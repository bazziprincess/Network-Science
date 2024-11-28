import networkx as nx
import matplotlib.pyplot as plt

def load_network(gml_file):
    G = nx.read_gml(gml_file)
    print(f"Graph loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges.")
    return G

def plot_directed_network(G, top_n=10, threshold=20):
    """Draw a directed network graph and mark high traffic sites"""

    filtered_edges = [(u, v) for u, v, d in G.edges(data=True) if d['weight'] >= threshold]
    filtered_nodes = {node for edge in filtered_edges for node in edge}
    subgraph = G.subgraph(filtered_nodes)

    total_flow = {node: G.degree(node, weight='weight') for node in subgraph.nodes}

    # Find the top_n high traffic sites
    top_stations = sorted(total_flow.items(), key=lambda x: x[1], reverse=True)[:top_n]
    top_nodes = [station for station, _ in top_stations]

    top_labels = {station: str(rank + 1) for rank, (station, _) in enumerate(top_stations)}
    station_info = "\n".join([f"{rank + 1}. {station}" for rank, (station, _) in enumerate(top_stations)])


    print(f"Top {top_n} high-traffic stations:")
    for station, flow in top_stations:
        print(f"{station}: {flow}")

    node_size = [total_flow[node] * 1.5 for node in subgraph.nodes]
    node_color = ['#FFA500' if node in top_nodes else 'lightblue' for node in subgraph.nodes]
    pos = nx.spring_layout(subgraph, seed=42, k=1.2) 

    plt.figure(figsize=(20, 20))

    nx.draw_networkx_nodes(
        subgraph, pos,
        node_size=node_size,
        node_color=node_color,
        edgecolors="darkblue",
        linewidths=1.2,
        alpha=0.9
    )

    edge_width = [subgraph[u][v]['weight'] * 0.02 for u, v in subgraph.edges]
    nx.draw_networkx_edges(
        subgraph, pos,
        width=edge_width,
        edge_color="gray",
        alpha=0.4,
        arrows=True
    )

    # Draw labels for top nodes with ranking numbers
    nx.draw_networkx_labels(
        subgraph, pos,
        labels=top_labels,
        font_size=12,
        font_color='black',
        font_weight='bold'
    )

    plt.text(
        0.9, 1.0, f"Top Traffic Stations:\n{station_info}",
        fontsize=10,
        horizontalalignment='left',
        verticalalignment='top',
        transform=plt.gca().transAxes,
        bbox=dict(boxstyle="round,pad=0.3", edgecolor="gray", facecolor="white")
    )

    plt.title("Bike Sharing Network", fontsize=20)
    plt.axis("off")

    # Save the plot
    plt.savefig("1week_bike_network_plot.png", dpi=300, bbox_inches='tight')

    plt.show()

def main():
    gml_file = '1week_bike_network.gml'
    G = load_network(gml_file)
    plot_directed_network(G, top_n=10, threshold=0)

if __name__ == "__main__":
    main()
