import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

G = nx.Graph()

links = pd.read_csv('TopologiasDeReferencia/usaGde_links.csv')
nodes = pd.read_csv('TopologiasDeReferencia/usaGde_nodes.csv')

# nodes
id, latitude, longitude, type = nodes['Id'], nodes['Lat'], nodes['Long'], nodes['Type']
# links
From, to, length, capacity, cost = links['From'], links['To'], links['Length'], links['Capacity'], links['Cost']

for i in range(len(id)):
    G.add_node(id[i],
               pos=(
        float(longitude[i]),
        float(latitude[i]),
    ),
        type=str(type[i])
    )

for i in range(len(From)):
    G.add_edge(From[i], to[i],
               length=float(length[i]),
               capacity=float(capacity[i]),
               cost=float(cost[i])
               )


def nodesNumber():
    return G.number_of_nodes()


def edgesNumber():
    return G.number_of_edges()


def mediumDegree():
    return G.


pos = nx.get_node_attributes(G, 'pos')
edge_labels = {(u, v): d['cost'] for u, v, d in G.edges(data=True)}

nx.draw(G, pos, with_labels=True)
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

print(nodesNumber())

plt.show()
