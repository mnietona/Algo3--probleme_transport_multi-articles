import pandas as pd
import sys
import networkx as nx
import matplotlib.pyplot as plt
from statistics import median

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
    """ Lit les données d'instance du fichier. """
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

def save_model(data, filename, aggregated):
    """Sauvegarde le modèle dans un fichier."""
    model_str = generate_model(data, aggregated)
    with open(filename, 'w') as file:
        file.write(model_str)

def generate_model(data, aggregated):
    """Génère le modèle linéaire, agrégé ou désagrégé."""
    model_str = "Minimize\nobj:"
    model_str = calculate_edge_costs(data, model_str, aggregated=aggregated)

    model_str += "\n\nSubject To"
    model_str = model_constraints(data, model_str, aggregated=aggregated)

    model_str += "\n\nBounds\n"
    model_str = define_decision_variable_bounds(data, model_str, aggregated=aggregated)

    model_str += "\nGenerals\n"
    model_str = define_variable_types(data, model_str, aggregated=aggregated)

    model_str += "\nEnd"
    return model_str

def verify_balanced(data, aggregated=True):
    """ Verifie si le problème est équilibré. """
    if not aggregated:
        balance_status = {}
        for i in range(data['items']):
            balance_status[i] = check_balance(data, f'CAPACITY_ITEM_{i}', f'DEMAND_ITEM_{i}')
        return balance_status
    else:
        return check_balance(data, 'CAPACITY', 'DEMAND')
    
def check_balance(data, supply_key, demand_key):
    """ Vérifie si l'offre est égale à la demande. """
    total_supply = total_demand = 0
    for _, df in data.items():
        if isinstance(df, pd.DataFrame):
            supply_columns = [col for col in df.columns if supply_key in col]
            demand_columns = [col for col in df.columns if demand_key in col]
            for col in supply_columns:
                total_supply += df[col].sum()
            for col in demand_columns:
                total_demand += df[col].sum()
    

    if total_supply == total_demand:
        return "=", "="
    elif total_supply > total_demand:
        return "<=", "="
    else:
        return "=", "<="

def calculate_edge_costs(data, model_str, aggregated=True):
    """
    Calcule et ajoute les coûts par arc.
    Si mode='aggregated', utilise la médiane des coûts pour un coût représentatif.
    Si mode='disaggregated', calcule les coûts par item et les ajoute pour chaque item.
    """
    for _, edge in data['edges'].iterrows():
        if aggregated:
            costs = [float(edge[f'COST_ITEM_{i}']) for i in range(data['items'])]
            representative_cost = median(costs)
            model_str += f" {'-' if representative_cost < 0 else '+'} {abs(representative_cost)} x{edge['ID']}"
        else:
            for i in range(data['items']):
                cost = float(edge[f'COST_ITEM_{i}'])
                model_str += f" {'-' if cost < 0 else '+'} {abs(cost)} x{edge['ID']}_{i}"
    return model_str

def get_intermediate_nodes(data):
    """ Renvoie les nœuds intermédiaires du graphe. """
    all_nodes = set(data['edges']['START']).union(set(data['edges']['END']))
    sources = set(data['sources']['ID'])
    destinations = set(data['destinations']['ID'])
    intermediate_nodes = all_nodes - sources - destinations
    return intermediate_nodes

def get_edge_str(edges, ids, item_suffix):
    """Crée un str de la forme 'x1 + x2 + ...' pour les arcs donnés."""
    return " + ".join([f"x{edge_id}{item_suffix}" for edge_id in ids if edge_id in set(edges['ID'])])

def clean_edge_str(outgoing_edge_str, incoming_edge_str):
    """ Nettoie les str en supprimant les ID communs."""
    all_edges = outgoing_edge_str.split(' + ') + incoming_edge_str.split(' + ')
    edge_count = {}

    for edge in all_edges:
        if edge in edge_count:
            edge_count[edge] += 1
        else:
            edge_count[edge] = 1

    outgoing_edges_cleaned = ' + '.join(edge for edge in outgoing_edge_str.split(' + ') if edge_count[edge] == 1)
    incoming_edges_cleaned = ' + '.join(edge for edge in incoming_edge_str.split(' + ') if edge_count[edge] == 1)

    return outgoing_edges_cleaned, incoming_edges_cleaned

def create_constraint_string(constraint_type, constraint_sign, node_id, suffix, outgoing_edge_str, incoming_edge_str, capacity_or_demand):
    """ Crée une contrainte de capacité ou de demande pour un nœud donné. """
    if 'source' in constraint_type:
        incoming_edge_str = incoming_edge_str.replace('+', '-')
        flow_expr = f"{outgoing_edge_str} - {incoming_edge_str}" if incoming_edge_str else f"{outgoing_edge_str}"
        sign = constraint_sign[0] 
    else:  # 'destination'
        outgoing_edge_str = outgoing_edge_str.replace('+', '-')
        flow_expr = f"{incoming_edge_str} - {outgoing_edge_str}" if outgoing_edge_str else f"{incoming_edge_str}"
        sign = constraint_sign[1] 

    constraint_name = 'cap' if 'source' in constraint_type else 'demand'
    return f"\n{constraint_name}_{node_id}{suffix}: {flow_expr} {sign} {capacity_or_demand}"
            
def process_constraints(data, model_str, constraint_type, signes, aggregated=True):
    """Traite les contraintes pour les sources et les destinations."""
    nodes = data[constraint_type]
    node_type_id = 'ID'
    
    for _, node in nodes.iterrows():
        node_id = node[node_type_id]
        item_range = range(data['items']) if not aggregated else [None]

        for i in item_range:
            suffix = f"_{i}" if not aggregated else ""
            key = 'CAPACITY_ITEM_' if 'source' in constraint_type else 'DEMAND_ITEM_'
            capacity_or_demand = node[f'{key}{i}'] if not aggregated else sum([node[f'{key}{j}'] for j in range(data['items'])])

            outgoing_edges = data['edges'][data['edges']['START'] == node_id]
            incoming_edges = data['edges'][data['edges']['END'] == node_id]

            outgoing_edge_str = get_edge_str(outgoing_edges, outgoing_edges['ID'], suffix)
            incoming_edge_str = get_edge_str(incoming_edges, incoming_edges['ID'], suffix)
            
            outgoing_edge_str, incoming_edge_str = clean_edge_str(outgoing_edge_str, incoming_edge_str)
            constraint_sign = signes[i] if not aggregated else signes
            
            model_str += create_constraint_string(constraint_type, constraint_sign, node_id, suffix, outgoing_edge_str, incoming_edge_str, capacity_or_demand)

    return model_str

def intermediate_nodes_flow_constraints(data, model_str, aggregated=True):
    """ Traite les contraintes de flux pour les nœuds intermédiaires. """
    intermediate_nodes = get_intermediate_nodes(data)
    for node in intermediate_nodes:
        item_range = range(data['items']) if not aggregated else [None]
        
        for i in item_range:
            suffix = f"_{i}" if not aggregated else ""
        
            incoming_edges = data['edges'][data['edges']['END'] == node]
            outgoing_edges = data['edges'][data['edges']['START'] == node]
            
            incoming_edge_str = get_edge_str(incoming_edges, incoming_edges['ID'], suffix)
            outgoing_edge_str = get_edge_str(outgoing_edges, outgoing_edges['ID'], suffix)
            
            incoming_edge_str, outgoing_edge_str = clean_edge_str(incoming_edge_str, outgoing_edge_str)
            outgoing_edge_str = outgoing_edge_str.replace('+', '-')
            
            model_str += f"\nflow_{node}{suffix}: {incoming_edge_str} - {outgoing_edge_str} = 0"

    return model_str

def model_constraints(data, model_str, aggregated=True): 
    """ Traite toutes les contraintes du modèle. """
    balance_signs = verify_balanced(data, aggregated=aggregated)
    model_str = process_constraints(data, model_str, 'sources', balance_signs, aggregated=aggregated)
    model_str = intermediate_nodes_flow_constraints(data, model_str, aggregated=aggregated)
    model_str = process_constraints(data, model_str, 'destinations', balance_signs, aggregated=aggregated)
    return model_str

def define_decision_variable_bounds(data, model_str, aggregated=True):
    """ Définit les bornes des variables de décision. """
    for _, edge in data['edges'].iterrows():
        if aggregated:
            model_str += f"0 <= x{edge['ID']} <= +inf\n"
        else:
            for i in range(data['items']):
                model_str += f"0 <= x{edge['ID']}_{i} <= +inf\n"
    return model_str

def define_variable_types(data, model_str, aggregated=True):
    """ Définit le type des variables de décision. """
    for _, edge in data['edges'].iterrows():
        if aggregated:
            model_str += f"x{edge['ID']}\n"
        else:
            for i in range(data['items']):
                model_str += f"x{edge['ID']}_{i}\n"
    return model_str

def main():
    if len(sys.argv) != 3:
        print("Usage: python generate_model.py <instance_filename> <0 (aggregated) | 1 (disaggregated)>")
        sys.exit(1)

    instance_filename = sys.argv[1]
    filename = instance_filename.split('/')[-1]
    aggregated = int(sys.argv[2]) == 0 # True si agrégé, False si désagrégé

    # Lire les données d'instance
    data = read_instance(instance_filename)
    
    # Demander à l'utilisateur s'il veut un graph
    print("Voulez-vous afficher le graphe du problème ? (y/n)")
    user_input = input()
    if user_input == 'y':
        plot_graph(data)
    
    # Générer le fichier .lp
    lp_filename =  f"{filename[:-4]}_{sys.argv[2]}.lp"
    save_model(data, lp_filename, aggregated)
    
    # Déplacer le fichier dans le dossier parent  #### A RETIRER POUR LA REMISE
    import shutil
    shutil.move(lp_filename, f"../{lp_filename}")
    
if __name__ == "__main__":
    main()
