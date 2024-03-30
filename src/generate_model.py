import pandas as pd
import sys

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
    num_items = data['items']
    
    model_str = "Minimize\nobj:"

    # Fonction objectif
    for index, edge in data['edges'].iterrows():
        for i in range(num_items):
            # verfier si cost negatif alors - et non +
            cost_item_i = float(edge[f'COST_ITEM_{i}'])
            if cost_item_i < 0:
                model_str += f" {cost_item_i} x{edge['ID']}_item{i}"
            else:
                model_str += f" + {cost_item_i} x{edge['ID']}_item{i}"


    model_str += "\n\nSubject To\n"

    # Contraintes de capacité des sources
    for index, source in data['sources'].iterrows():
        for i in range(num_items):
            constraint_str = ""
            for _, edge in data['edges'].iterrows():
                if edge['START'] == source['ID']:
                    constraint_str += f" + x{edge['ID']}_item{i}"
            if constraint_str:  # Add the constraint if it's not empty
                model_str += f" c{source['ID']}_capacity_item{i}:{constraint_str} <= {source[f'CAPACITY_ITEM_{i}']}\n"

    # Contraintes de demande des destinations
    for index, destination in data['destinations'].iterrows():
        for i in range(num_items):
            constraint_str = ""
            for _, edge in data['edges'].iterrows():
                if edge['END'] == destination['ID']:
                    constraint_str += f" + x{edge['ID']}_item{i}"
            if constraint_str:  # Add the constraint if it's not empty
                model_str += f" c{destination['ID']}_demand_item{i}:{constraint_str} >= {destination[f'DEMAND_ITEM_{i}']}\n"

    # Contraintes de non-négativité
    model_str += "\nBounds\n"
    for _, edge in data['edges'].iterrows():
        for i in range(num_items):
            model_str += f" 0 <= x{edge['ID']}_item{i}\n"

    model_str += "\nEnd\n"
    
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
    #print_data(data)

    # Générer le fichier .lp
    lp_filename =  f"{filename[:-4]}_{sys.argv[2]}.lp"
    save_model(data, lp_filename, aggregated)
    
