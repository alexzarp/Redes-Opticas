import itertools
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

G = nx.Graph()

# links = pd.read_csv('TopologiasDeReferencia/usaGde_links.csv')
# nodes = pd.read_csv('TopologiasDeReferencia/usaGde_nodes.csv')
links = pd.read_csv('TopologiasDeReferencia/fake_links.csv')
nodes = pd.read_csv('TopologiasDeReferencia/fake_nodes.csv')
# links = pd.read_csv('TopologiasDeReferencia/rnpBrazil_links-2023.csv')
# nodes = pd.read_csv('TopologiasDeReferencia/rnpBrazil_nodes-2023.csv')
demandas = pd.read_csv('Demandas/fake_demandas.csv')

# nodes
id, latitude, longitude, type = nodes['Id'], nodes['Lat'], nodes['Long'], nodes['Type']
# links
From, to, length, capacity, cost = links['From'], links['To'], links['Length'], links['Capacity'], links['Cost']
# demandas
Source, Destination, Demand = demandas['Source'], demandas['Destination'], demandas['Demand']

CC = 12.5 # tamanho do canal
channels = []
for i in range(0, 80):
    new_dict = {'State': False, 'From': '', 'to': ''}
    channels.append(new_dict)

def changeChannel(vet, flag, ch = []):
    if ch == []:
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
        
def unchangeChannel(vet, ch = []):
    if ch == []:
        for idx, slot in enumerate(vet):
            if slot['State']:
                slot['State'] = False
                vet[idx + 1]['State'] = False
                break
    else:
        vet[ch[0]]['State'] = False
        vet[ch[1]]['State'] = False

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

def drawGraph(G):
    pos = nx.get_node_attributes(G, 'pos')
    edge_labels = {(u, v): d['cost'] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
    nx.draw(G, pos, with_labels=True, edge_color='black', width=1, alpha=0.5, node_size=500, node_color='blue')
    plt.show()
drawGraph(G)

def testDemands():
    for i in range(len(Source)):
        print('Demanda de {} para {} com {}Gbps'.format(Source[i], Destination[i], Demand[i]))
        print('Taxa de bloqueio: {}%'.format(TB(mapNetwork(Source[i]), Demand[i])))
        print()

# path = nx.dijkstra_path(G, 'Miami', 'Portland', weight='cost')
# print(G.edges['Miami', 'Jupiter']['cost'])
# print(mapNetwork('Porto Alegre'))

def calculate_total_extension(G):
    total_extension = 0
    for u, v in G.edges():
        position_u = G.nodes[u]['pos']
        position_v = G.nodes[v]['pos']
        length = G.edges[u, v]['length']
        total_extension += length * distance(position_u, position_v)
    return total_extension

def distance(pos1, pos2): # Distancia por latitudes e longitudes euclidianas
    return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5

def test_all_node_positions(G):
    best_extension = float('inf')
    best_configuration = None

    nodes = list(G.nodes())
    positions = list(itertools.permutations(nodes))

    for pos in positions:
        for i, node in enumerate(nodes):
            G.nodes[node]['pos'] = G.nodes[pos[i]]['pos']

        total_extension = calculate_total_extension(G)

        if total_extension < best_extension:
            best_extension = total_extension
            best_configuration = pos

    return best_configuration

def replace_node_positions(G, best_configuration):
    # Salvar a posição atual dos nós em uma variável temporária
    old_positions = nx.get_node_attributes(G, 'pos')
  
    # Criar um novo grafo com os nós reordenados
    new_G = nx.Graph()
    for i, node in enumerate(best_configuration):
        new_G.add_node(node, pos=old_positions[i])
  
    # Atualizar as arestas do novo grafo
    new_edges = []
    for u, v, data in G.edges(data=True):
        new_u = best_configuration.index(u)
        new_v = best_configuration.index(v)
        new_data = dict(data)
        new_edges.append((new_u, new_v, new_data))
    new_G.add_edges_from(new_edges)
  
    # Substituir o grafo G pelo novo grafo com nós reordenados
    G.clear()
    G.add_edges_from(new_G.edges(data=True))
    G.add_nodes_from(new_G.nodes(data=True))

# Exemplo de uso:
best_configuration = test_all_node_positions(G)
print("Melhor configuração de nós:")
print(best_configuration)

testDemands()

# Exemplo de uso:
print("Grafo com nós reordenados:")
replace_node_positions(G, best_configuration)
drawGraph(G)
plt.show()