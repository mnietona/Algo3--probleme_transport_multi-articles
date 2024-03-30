import pandas as pd
import sys
import networkx as nx
import matplotlib.pyplot as plt

def plot_graph(data):
    """ Code pour afficher le graphe du problème. Donnée par ChatGpt """
    G = nx.DiGraph()

    # Ajout des noeuds avec leurs positions
    for index, node in data['nodes'].iterrows():
        G.add_node(node['ID'], pos=(node['x'], node['y']))

    # Ajout des arêtes
    for index, edge in data['edges'].iterrows():
        G.add_edge(edge['START'], edge['END'], weight=edge['COST_ITEM_0'])

    pos = nx.get_node_attributes(G, 'pos')
    # je veux un bleu claire 
    nx.draw(G, pos, with_labels=True, node_size=500, node_color='lightblue', font_size=8)

    # Colorier les noeuds sources en vert et les noeuds destinations en rouge
    source_nodes = data['sources']['ID'].tolist()
    destination_nodes = data['destinations']['ID'].tolist()
    
    nx.draw_networkx_nodes(G, pos, nodelist=source_nodes, node_color='green', node_size=500)
    nx.draw_networkx_nodes(G, pos, nodelist=destination_nodes, node_color='red', node_size=500)

    plt.show()

def read_section(file, nb_items, columns):
    """Lit une section spécifique du fichier et renvoie un DataFrame pandas."""
    data = []
    for _ in range(nb_items):
        item_data = next(file).strip().split()
        data.append([float(x) if '.' in x else int(x) if x.isdigit() else x for x in item_data])
    return pd.DataFrame(data, columns=columns)

def read_instance(filename):
    data = {}
    with open(filename, 'r') as file:
        for line in file:
            
            line = line.strip().split(' ')
            key, nb_items = line[0], line[1] if len(line) > 1 else None
            
            if key == 'ITEMS':
                data['items'] = int(nb_items)
            elif nb_items is not None:
                header = next(file).strip().split()
                nb_items = int(nb_items)
                data[key.lower()] = read_section(file, nb_items, header)
    return data

def generate_aggregated_model(data):
    """Génère le modèle agrégé."""
    model_str = "Minimize\nobj:"
    first_term = True

    # Calcul du coût représentatif pour chaque arc
    for index, edge in data['edges'].iterrows():
        costs = [float(edge[f'COST_ITEM_{i}']) for i in range(data['items'])]
        representative_cost = sum(costs) / len(costs)  # Utilisation de la moyenne comme coût représentatif
        if first_term:
            model_str += f" {abs(representative_cost)} x{edge['ID']}"
            first_term = False
        else:
            model_str += f" + {abs(representative_cost)} x{edge['ID']}"

    model_str += "\n\nSubject To\n"

    # Agrégation et contraintes de capacité pour chaque source
    for index, source in data['sources'].iterrows():
        total_capacity = sum([source[f'CAPACITY_ITEM_{i}'] for i in range(data['items'])])
        model_str += f"\ncap_{source['ID']}: "
        outgoing_edges = data['edges'][data['edges']['START'] == source['ID']]
        for _, edge in outgoing_edges.iterrows():
            model_str += f" + x{edge['ID']}"
        model_str += f" <= {total_capacity}"

    # Agrégation et contraintes de demande pour chaque destination
    for index, destination in data['destinations'].iterrows():
        total_demand = sum([destination[f'DEMAND_ITEM_{i}'] for i in range(data['items'])])
        model_str += f"\ndemand_{destination['ID']}: "
        incoming_edges = data['edges'][data['edges']['END'] == destination['ID']]
        for _, edge in incoming_edges.iterrows():
            model_str += f" + x{edge['ID']}"
        model_str += f" = {total_demand}"

    # Variables de décision et leurs bornes
    model_str += "\n\nBounds\n"
    for _, edge in data['edges'].iterrows():
        model_str += f"0 <= x{edge['ID']} <= +inf\n"

    # Définition du type des variables
    model_str += "\nGenerals\n"
    for _, edge in data['edges'].iterrows():
        model_str += f"x{edge['ID']}\n"

    model_str += "\nEnd"
    return model_str

def generate_disaggregated_model(data):
    """Génère le modèle désagrégé."""
    # Construction du modèle CPLEX LP désagrégé
    model_str = ""
    # Ajoutez la construction du modèle ici
    return model_str

def save_model(data, filename, aggregated):
    """Sauvegarde le modèle dans un fichier."""
    if aggregated:
        model_str = generate_aggregated_model(data)
    else:
        model_str = generate_disaggregated_model(data)
    with open(filename, 'w') as file:
        file.write(model_str)
    
    #### Déplacer le fichier dans le dossier parent
    import shutil
    shutil.move(filename, f"../{filename}")

def print_data(data):
    for key, value in data.items():
        print(key)
        print(value)
        print()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_model.py <instance_filename> <0 (aggregated) | 1 (disaggregated)>")
        sys.exit(1)

    instance_filename = sys.argv[1]
    filename = instance_filename.split('/')[-1]
    aggregated = int(sys.argv[2]) == 0  # Convertit le deuxième argument en booléen pour choisir le modèle

    # Lire les données d'instance
    data = read_instance(instance_filename)
    #plot_graph(data)
    #print_data(data)

    # Générer le fichier .lp
    lp_filename =  f"{filename[:-4]}_{sys.argv[2]}.lp"
    save_model(data, lp_filename, aggregated)