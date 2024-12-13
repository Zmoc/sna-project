import cudf
import cugraph
import graph_tool.all as gt

# Load the graph data (CSV containing edges)
edges_df = cudf.read_csv(
    "Documents/1 - Projects/codingProjects/sna-project/data/cleanedData/user.csv",
    header=True,
)

# Assign appropriate column names
edges_df.columns = ["userID", "friendID"]
nodeDataPath = (
    "Documents/1 - Projects/codingProjects/sna-project/data/cleanedData/nodeData.csv"
)
graphDataPath = (
    "Documents/1 - Projects/codingProjects/sna-project/data/cleanedData/graphData.csv"
)

# Create a cuGraph graph from the edges
G = cugraph.Graph()
G.from_cudf_edgelist(edges_df, source="userID", destination="friendID")

numNodes = G.number_of_vertices()
print(f"Number of nodes: {numNodes}")
numEdges = G.number_of_edges()
print(f"Number of edges: {numEdges}")
density = G.density()
print(f"Graph density: {density}")
degree = G.degree()
print(f"Degree Sample: {degree.head()}")
degreeCentrality = G.degree()
degreeCentrality["degree"] /= degreeCentrality["degree"].max()
print(f"Degree Centrality Sample: {degreeCentrality.head()}")

graphData = cudf.DataFrame([numNodes, numEdges, density])
graphData.to_csv(graphDataPath, chunksize=10000)

nodeDegree = cudf.DataFrame(degree)
nodeDegreeCent = cudf.DataFrame(degreeCentrality)
nodeData = cudf.concat([nodeDegree, nodeDegreeCent])
nodeData.to_csv(nodeDataPath, chunksize=10000)
