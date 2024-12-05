import pandas as pd
import pygraphviz as pgv

# File path
friendEdgePath = "data/cleanedData/sampleFriendEdge.csv"

# Initialize a PyGraphviz graph
G = pgv.AGraph(strict=False, directed=False)

# Load the edge list in chunks and add edges
chunksize = 1_000_000
edge_chunks = pd.read_csv(
    friendEdgePath, header=None, names=["source", "target"], chunksize=chunksize
)

for chunk in edge_chunks:
    # Add only edges; nodes without edges won't be added
    G.add_edges_from(chunk.values)

# Compute degrees for all nodes
node_degrees = {node: G.degree(node) for node in G.nodes()}

# Get the top 20 nodes by degree
top_20_nodes = sorted(node_degrees.items(), key=lambda x: x[1], reverse=True)[:20]
top_20_node_set = {node for node, _ in top_20_nodes}

# Initialize the set of nodes to include in the subgraph (top 20 nodes + their neighbors)
nodes_to_include = set(top_20_node_set)

# Include neighbors of the top 20 nodes
for node in top_20_node_set:
    neighbors = G.neighbors(node)
    nodes_to_include.update(neighbors)

# Create a new subgraph with only the top 20 nodes and their neighbors
SubG = G.subgraph(nodes_to_include)

# Define attributes for the subgraph
leaf_node_color = "red"
default_node_color = "blue"

for node in SubG.nodes():
    degree = SubG.degree(node)
    # Color leaf nodes red
    SubG.get_node(node).attr["color"] = (
        leaf_node_color if degree == 1 else default_node_color
    )
    # Adjust node size (base size + degree scaling)
    node_size = 5 + degree * 2
    SubG.get_node(node).attr["width"] = node_size / 10  # Node size in inches
    SubG.get_node(node).attr["height"] = node_size / 10

# Layout and save the subgraph visualization with increased spacing
output_path = "top_20_and_neighbors_visualization_spread.png"

# Use the 'neato' layout, which is often better for spreading nodes
SubG.layout(prog="sfdp")  # 'neato' generally spreads out nodes evenly

# Increase the DPI (resolution) and the size of the graph for better visibility
SubG.graph_attr["dpi"] = "300"  # Higher resolution for better quality
SubG.graph_attr["size"] = "10,10"  # Graph size in inches, increase if necessary

# Save the visualization
SubG.draw(output_path)
print(
    f"Graph visualization showing top 20 nodes and their neighbors with better spacing saved to {output_path}"
)
