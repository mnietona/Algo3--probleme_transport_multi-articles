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
    model_str = calculate_representative_edge_costs(data, model_str)

    model_str += "\n\nSubject To"
    source_sign, destination_sign = verify_balanced_aggregated(data)
    model_str = source_capacity_constraint(data, model_str, source_sign)
    
    all_nodes = set(data['edges']['START']).union(set(data['edges']['END']))
    sources = set(data['sources']['ID'])
    destinations = set(data['destinations']['ID'])
    intermediate_nodes = all_nodes - sources - destinations
    model_str = intermediate_nodes_flow_constraints(data, intermediate_nodes, model_str)
    
    model_str = destination_demand_constraints(data, destination_sign, model_str)
    
    model_str += "\n\nBounds\n"
    model_str = define_decision_variable_bounds(data, model_str)
    
    model_str += "\nGenerals\n"
    model_str = define_variable_types(data, model_str)

    model_str += "\nEnd"
    return model_str

def verify_balanced_aggregated(data):
    """Vérifie si le problème est équilibré."""
    total_supply = 0 
    total_demand = 0
    
    for _, df in data.items():
        if isinstance(df, pd.DataFrame):
            for column in df.columns:
                if 'CAPACITY' in column:
                    total_supply += df[column].sum()
                elif 'DEMAND' in column:
                    total_demand += df[column].sum()

    if total_supply == total_demand:
        return "=", "="
    elif total_supply > total_demand:
        return  "<=", "="
    else:
        return  "=" ,"<="
    
def calculate_representative_edge_costs(data, model_str):
    """ Calcule le coût représentatif de chaque arc. """
    for _, edge in data['edges'].iterrows():
        costs = [float(edge[f'COST_ITEM_{i}']) for i in range(data['items'])]
        representative_cost = median(costs)  # médiane comme coût représentatif
        model_str += f" {'-' if representative_cost < 0 else '+'} {abs(representative_cost)} x{edge['ID']}"
    return model_str

def source_capacity_constraint(data, model_str, source_signe):
    """Capacity constraints for each source, accounting for incoming and outgoing edges."""
    for _, source in data['sources'].iterrows():
        total_capacity = sum([source[f'CAPACITY_ITEM_{i}'] for i in range(data['items'])])
        model_str += f"\ncap_{source['ID']}: "

        outgoing_edges = data['edges'][data['edges']['START'] == source['ID']]
        incoming_edges = data['edges'][data['edges']['END'] == source['ID']]
        
        outgoing_edge_ids = set(outgoing_edges['ID'])
        incoming_edge_ids = set(incoming_edges['ID'])

        common_edge_ids = outgoing_edge_ids & incoming_edge_ids
        outgoing_edge_ids -= common_edge_ids
        incoming_edge_ids -= common_edge_ids

        outgoing_edge_str = " + ".join([f"x{edge_id}" for edge_id in outgoing_edge_ids])
        incoming_edge_str = " - ".join([f"x{edge_id}" for edge_id in incoming_edge_ids])

        if incoming_edge_str:
            model_str += f"{outgoing_edge_str} - {incoming_edge_str} {source_signe} {total_capacity}"
        else:
            model_str += f"{outgoing_edge_str} {source_signe} {total_capacity}"
    return model_str

def intermediate_nodes_flow_constraints(data, intermediate_nodes, model_str):
    """ Contraintes de conservation de flux pour chaque noeud intermédiaire."""
    for node in intermediate_nodes:
        in_edges = data['edges'][data['edges']['END'] == node]
        out_edges = data['edges'][data['edges']['START'] == node]
        in_edge_ids = {edge['ID'] for _, edge in in_edges.iterrows()}
        out_edge_ids = {edge['ID'] for _, edge in out_edges.iterrows()}

        common_edge_ids = in_edge_ids & out_edge_ids
        in_edge_ids -= common_edge_ids
        out_edge_ids -= common_edge_ids

        in_flow_str = " + ".join([f"x{edge_id}" for edge_id in in_edge_ids])
        out_flow_str = " - ".join([f"x{edge_id}" for edge_id in out_edge_ids])

        model_str += f"\nflow_cons_{node}: {in_flow_str} - {out_flow_str} = 0"
    return model_str

def destination_demand_constraints(data, destination_signe, model_str):
    """ Contraintes de demande pour chaque destination, incluant les arcs entrants et sortants."""
    for _, destination in data['destinations'].iterrows():
        demands = [destination[f'DEMAND_ITEM_{i}'] for i in range(data['items'])]
        total_demand = sum(demands)
        model_str += f"\ndemand_{destination['ID']}: "

        incoming_edges = data['edges'][data['edges']['END'] == destination['ID']]
        outgoing_edges = data['edges'][data['edges']['START'] == destination['ID']]
        
        outgoing_edge_ids = set(outgoing_edges['ID'])
        incoming_edge_ids = set(incoming_edges['ID'])

        common_edge_ids = outgoing_edge_ids & incoming_edge_ids
        outgoing_edge_ids -= common_edge_ids
        incoming_edge_ids -= common_edge_ids

        incoming_edge_str = " + ".join([f"x{edge_id}" for edge_id in incoming_edge_ids])
        outgoing_edge_str = " - ".join([f"x{edge_id}" for edge_id in outgoing_edge_ids])
        
        if outgoing_edge_str:
            model_str += f"{incoming_edge_str} - {outgoing_edge_str} {destination_signe} {total_demand}"
        else:
            model_str += f"{incoming_edge_str} {destination_signe} {total_demand}"
    return model_str

def define_decision_variable_bounds(data, model_str):
    """ Définit les bornes des variables de décision. """
    for _, edge in data['edges'].iterrows():
        model_str += f"0 <= x{edge['ID']} <= +inf\n"
    return model_str

def define_variable_types(data, model_str):
    """ Définit le type des variables de décision. """
    for _, edge in data['edges'].iterrows():
        model_str += f"x{edge['ID']}\n"
    return model_str

def generate_disaggregated_model(data):
    """Génère le modèle désagrégé."""
    model_str = "Minimize\nobj:"
    model_str = calculate_edge_costs_by_item(data, model_str)

    model_str += "\n\nSubject To"
    balance_status = verify_balanced_disaggregated(data)
    
    model_str = source_capacity_constraint_by_item(data, balance_status, model_str)

    all_nodes = set(data['edges']['START']).union(set(data['edges']['END']))
    sources = set(data['sources']['ID'])
    destinations = set(data['destinations']['ID'])
    intermediate_nodes = all_nodes - sources - destinations
    model_str = intermediate_nodes_flow_constraints_by_item(data, intermediate_nodes, model_str)

    model_str = destination_demand_constraints_by_item(data, balance_status, model_str)

    model_str += "\n\nBounds\n"
    model_str = define_decision_variable_bounds_by_item(data, model_str)
    
    model_str += "\nGenerals\n"
    model_str = define_variable_types_by_item(data, model_str)

    model_str += "\nEnd"
    return model_str

def verify_balanced_disaggregated(data):
    """Vérifie si le problème est équilibré pour chaque type d'article."""
    balance_status = {}

    total_supply = {i: 0 for i in range(data['items'])}
    total_demand = {i: 0 for i in range(data['items'])}

    for _, df in data.items():
        if isinstance(df, pd.DataFrame):
            for i in range(data['items']):
                capacity_columns = [col for col in df.columns if f'CAPACITY_ITEM_{i}' in col]
                demand_columns = [col for col in df.columns if f'DEMAND_ITEM_{i}' in col]
                
                for col in capacity_columns:
                    total_supply[i] += df[col].sum()
                for col in demand_columns:
                    total_demand[i] += df[col].sum()

    for i in range(data['items']):
        if total_supply[i] == total_demand[i]:
            balance_status[i] = ("=", "=")
        elif total_supply[i] > total_demand[i]:
            balance_status[i] = ("<=", "=")
        else:
            balance_status[i] = ("=", "<=")

    return balance_status
    
def calculate_edge_costs_by_item(data, model_str):
    """Calcule et ajoute les coûts par arc et par type d'article."""
    for _, edge in data['edges'].iterrows():
        for i in range(data['items']):
            cost = float(edge[f'COST_ITEM_{i}'])
            model_str += f" {'-' if cost < 0 else '+'} {abs(cost)} x{edge['ID']}_{i}"
    return model_str

def source_capacity_constraint_by_item(data, balance_status, model_str):
    """Capacity constraints for each source and each item type, ensuring no overlap in edge IDs for in-flow and out-flow."""
    for _, source in data['sources'].iterrows():
        for i in range(data['items']):
            capacity = source[f'CAPACITY_ITEM_{i}']
            outgoing_edges = data['edges'][data['edges']['START'] == source['ID']]
            incoming_edges = data['edges'][data['edges']['END'] == source['ID']]

            outgoing_edge_ids = set(outgoing_edges['ID'])
            incoming_edge_ids = set(incoming_edges['ID'])

            common_edge_ids = outgoing_edge_ids & incoming_edge_ids
            outgoing_edge_ids -= common_edge_ids
            incoming_edge_ids -= common_edge_ids

            outgoing_edge_str = " + ".join([f"x{edge.ID}_{i}" for edge in outgoing_edges.itertuples() if edge.ID in outgoing_edge_ids])
            incoming_edge_str = " - ".join([f"x{edge.ID}_{i}" for edge in incoming_edges.itertuples() if edge.ID in incoming_edge_ids])

            if incoming_edge_str:
                model_str += f"\ncap_{source['ID']}_{i}: {outgoing_edge_str} - {incoming_edge_str} {balance_status[i][0]} {capacity}"
            else:
                model_str += f"\ncap_{source['ID']}_{i}: {outgoing_edge_str} {balance_status[i][0]} {capacity}"
    return model_str

def intermediate_nodes_flow_constraints_by_item(data, intermediate_nodes, model_str):
    """Contraintes de conservation de flux pour chaque noeud intermédiaire et chaque type d'article."""
    for node in intermediate_nodes:
        for i in range(data['items']):
            in_edges = data['edges'][data['edges']['END'] == node]
            out_edges = data['edges'][data['edges']['START'] == node]
            
            in_edge_ids = {edge['ID'] for _, edge in in_edges.iterrows()}
            out_edge_ids = {edge['ID'] for _, edge in out_edges.iterrows()}
            
            common_edge_ids = in_edge_ids & out_edge_ids
            in_edge_ids -= common_edge_ids
            out_edge_ids -= common_edge_ids
            
            in_flow_str = " + ".join([f"x{edge_id}_{i}" for edge_id in in_edge_ids])
            out_flow_str = " - ".join([f"x{edge_id}_{i}" for edge_id in out_edge_ids])
            
            model_str += f"\nflow_cons_{node}_{i}: {in_flow_str} - {out_flow_str} = 0"

    return model_str

def destination_demand_constraints_by_item(data, balance_status, model_str):
    """Demand constraints for each destination and each item type, ensuring no overlap in edge IDs for incoming and outgoing flows."""
    for _, destination in data['destinations'].iterrows():
        for i in range(data['items']):
            demand = destination[f'DEMAND_ITEM_{i}']
            incoming_edges = data['edges'][data['edges']['END'] == destination['ID']]
            outgoing_edges = data['edges'][data['edges']['START'] == destination['ID']]

            incoming_edge_ids = set(incoming_edges['ID'])
            outgoing_edge_ids = set(outgoing_edges['ID'])

            common_edge_ids = incoming_edge_ids & outgoing_edge_ids
            incoming_edge_ids -= common_edge_ids
            outgoing_edge_ids -= common_edge_ids

            incoming_edge_str = " + ".join([f"x{edge.ID}_{i}" for edge in incoming_edges.itertuples() if edge.ID in incoming_edge_ids])
            outgoing_edge_str = " - ".join([f"x{edge.ID}_{i}" for edge in outgoing_edges.itertuples() if edge.ID in outgoing_edge_ids])

            if outgoing_edge_str:
                model_str += f"\ndemand_{destination['ID']}_{i}: {incoming_edge_str} - {outgoing_edge_str} {balance_status[i][1]} {demand}"
            else:
                model_str += f"\ndemand_{destination['ID']}_{i}: {incoming_edge_str} {balance_status[i][1]} {demand}"
    return model_str


def define_decision_variable_bounds_by_item(data, model_str):
    """Définit les bornes des variables de décision pour chaque arc et chaque type d'article."""
    for _, edge in data['edges'].iterrows():
        for i in range(data['items']):
            model_str += f"0 <= x{edge['ID']}_{i} <= +inf\n"
    return model_str

def define_variable_types_by_item(data, model_str):
    """Définit le type des variables de décision pour chaque arc et chaque type d'article."""
    for _, edge in data['edges'].iterrows():
        for i in range(data['items']):
            model_str += f"x{edge['ID']}_{i}\n"
    return model_str

def save_model(data, filename, aggregated):
    """Sauvegarde le modèle dans un fichier."""
    if aggregated:
        model_str = generate_aggregated_model(data)
    else:
        model_str = generate_disaggregated_model(data)
    with open(filename, 'w') as file:
        file.write(model_str)

def print_data(data):
    for key, value in data.items():
        print(key)
        print(value)
        print()

def main():
    if len(sys.argv) != 3:
        print("Usage: python generate_model.py <instance_filename> <0 (aggregated) | 1 (disaggregated)>")
        sys.exit(1)

    instance_filename = sys.argv[1]
    filename = instance_filename.split('/')[-1]
    aggregated = int(sys.argv[2]) == 0 # True si agrégé, False si désagrégé

    # Lire les données d'instance
    data = read_instance(instance_filename)
    

    # Générer le fichier .lp
    lp_filename =  f"{filename[:-4]}_{sys.argv[2]}.lp"
    save_model(data, lp_filename, aggregated)
    
    # Déplacer le fichier dans le dossier parent 
    import shutil
    shutil.move(lp_filename, f"../{lp_filename}")
    
    #plot_graph(data)
    
if __name__ == "__main__":
    main()
