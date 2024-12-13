import cudf
import cugraph
import graph_tool.all as gt
import pandas as pd

nodeDataPath = (
    "Documents/1 - Projects/codingProjects/sna-project/data/cleanedData/nodeData.csv"
)
graphDataPath = (
    "Documents/1 - Projects/codingProjects/sna-project/data/cleanedData/graphData.csv"
)
filteredDataPath = "Documents/1 - Projects/codingProjects/sna-project/data/cleanedData/filteredData.csv"
imagePath = "Documents/1 - Projects/codingProjects/sna-project/data/images/graph_visualization.png"

# Load the graph data (CSV containing edges)
edges_df = cudf.read_csv(
    "Documents/1 - Projects/codingProjects/sna-project/data/cleanedData/user.csv",
    header=True,
)
edges_df.columns = ["userID", "friendID"]

G = cugraph.Graph()
G.from_cudf_edgelist(edges_df, source="userID", destination="friendID")

degreeThresh = 500
degree = G.degree()
filteredNodes = degree[degree["degree"] > degreeThresh]

filteredEdges = edges_df[
    (edges_df["userID"].isin(filteredNodes["vertex"]))
    & (edges_df["friendID"].isin(filteredNodes["vertex"]))
]
edges_pd = filteredEdges.to_pandas()

subgraph = cugraph.Graph()
subgraph.from_cudf_edgelist(filteredEdges, source="userID", destination="friendID")

degreeCentrality = subgraph.degree()

# Normalize centrality values
degreeCentrality["degree"] /= degreeCentrality["degree"].max()
print(f"Degree Centrality Sample: {degreeCentrality.head()}")

betweenness = cugraph.betweenness_centrality(subgraph)
betweenness_pd = betweenness.to_pandas()
print(f"Betweenness Centrality: {betweenness.head()}")

dcData = cudf.DataFrame(degreeCentrality)
bcData = cudf.DataFrame(betweenness)
filterData = cudf.concat([dcData, bcData])
filterData.to_csv(filteredDataPath, chunksize=10000)

gt_graph = gt.Graph(directed=False)
vertex_map = {}

for node in pd.concat([edges_pd["userID"], edges_pd["friendID"]]).unique():
    vertex_map[node] = gt_graph.add_vertex()

for _, edge in edges_pd.iterrows():
    gt_graph.add_edge(vertex_map[edge["userID"]], vertex_map[edge["friendID"]])

betweenness_prop = gt_graph.new_vertex_property("float")
for _, row in betweenness_pd.iterrows():
    if row["vertex"] in vertex_map:
        betweenness_prop[vertex_map[row["vertex"]]] = row["betweenness_centrality"]

gt_graph.vp.betweenness = betweenness_prop

gt.graph_draw(
    gt_graph,
    vertex_fill_color=gt_graph.vp.betweenness,
    vertex_size=5,
    edge_pen_width=1.2,
    output_size=(1000, 1000),
    output=imagePath,
)
