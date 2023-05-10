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

channels = [
    {'State': False, 'From': '', 'to': ''}, 
    {'State': False, 'From': '', 'to': ''},
    {'State': False, 'From': '', 'to': ''},
    {'State': False, 'From': '', 'to': ''},
    {'State': False, 'From': '', 'to': ''},
    {'State': False, 'From': '', 'to': ''},
    {'State': False, 'From': '', 'to': ''},
    {'State': False, 'From': '', 'to': ''},
]

def changeChannel(vet, flag, ch = ['', '']):
    if ch == ['', '']:
        for idx, slot in enumerate(vet):
            if flag and not slot['State']:
                slot['State'] = True
                vet[idx + 1]['State'] = True
                break
            if not flag and slot['State']:
                slot['State'] = False
                vet[idx + 1]['State'] = False
                break
            if idx == len(vet) - 2:
                return False
        return True
    else:
        if not vet[ch[0]]['State'] and not vet[ch[1]]['State']:
            vet[ch[0]]['State'] = True
            vet[ch[1]]['State'] = True
            return True
        else:
            return False

def contUsedChannels(vet):
    count = 0
    for slot in vet:
        if slot['State']:
            count += 1
    return count


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
        channel=channels,
        length=float(length[i]),
        capacity=float(capacity[i]),
        cost=float(cost[i])
    )

def nodesNumber():
    return G.number_of_nodes()


def edgesNumber():
    return G.number_of_edges()


def mediumDegree():
    sum = 0
    for node in G.nodes:
        sum += G.degree[node]
    return sum / nodesNumber()

# Retorna a taxa de bloqueio
blocked_edges = []
def mapNetwork(From):
    ret = 0
    for to in G.nodes:
        path = nx.dijkstra_path(G, From, to, weight='cost')
        if From == to:
            continue
        for i in range(len(path) - 1):
            if not changeChannel(G.edges[path[i], path[i + 1]]['channel'], True):
                ret += 2
                blocked_edges.append((path[i], path[i + 1]))
    return ret

def TB(DB, TD):
    return DB / TD

pos = nx.get_node_attributes(G, 'pos')
edge_labels = {(u, v): d['cost'] for u, v, d in G.edges(data=True)}

nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
nx.draw(G, pos, with_labels=True, edge_color='black', width=1, alpha=0.5, node_size=500, node_color='blue')ptyo

# path = nx.dijkstra_path(G, 'Miami', 'Portland', weight='cost')
# print(G.edges['Miami', 'Jupiter']['cost'])
print(mapNetwork('Miami'))
plt.show()
