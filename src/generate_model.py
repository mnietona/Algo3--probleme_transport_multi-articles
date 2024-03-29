import pandas as pd
import sys


def read_section(file, nb_items, columns):
    """Lit une section spécifique du fichier et renvoie un DataFrame pandas."""
    data = []
    for _ in range(nb_items):
        item_data = next(file).strip().split()
        data.append([eval(x) if x.isdigit() or "." in x else x for x in item_data])
    return pd.DataFrame(data, columns=columns)

def read_instance(filename):
    data = {}
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith('ITEMS'):
                data['items'] = int(line.split()[1])
            elif line.startswith('NODES'):
                next(file)  # Sauter l'en-tête des colonnes
                nb_nodes = int(line.split()[1])
                data['nodes'] = read_section(file, nb_nodes, ['ID', 'x', 'y'])
            elif line.startswith('EDGES'):
                next(file)  # Sauter l'en-tête des colonnes
                nb_edges = int(line.split()[1])
                data['edges'] = read_section(file, nb_edges, ['ID', 'START', 'END', 'COST_ITEM_0', 'COST_ITEM_1'])
            elif line.startswith('SOURCES'):
                next(file)  # Sauter l'en-tête des colonnes
                nb_sources = int(line.split()[1])
                data['sources'] = read_section(file, nb_sources, ['ID', 'CAPACITY_ITEM_0', 'CAPACITY_ITEM_1'])
            elif line.startswith('DESTINATIONS'):
                next(file)  # Sauter l'en-tête des colonnes
                nb_destinations = int(line.split()[1])
                data['destinations'] = read_section(file, nb_destinations, ['ID', 'DEMAND_ITEM_0', 'DEMAND_ITEM_1'])
    return data



def generate_lp_file(data, filename, aggregated):
    # Implémentez la logique pour générer le fichier .lp ici
    # Utilisez le paramètre 'aggregated' pour choisir entre le modèle agrégé ou désagrégé
    pass

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_model.py <instance_filename> <0 (aggregated) | 1 (disaggregated)>")
        sys.exit(1)

    instance_filename = sys.argv[1]
    aggregated = int(sys.argv[2]) == 0  # Convertit le deuxième argument en booléen pour choisir le modèle

    # Lire les données d'instance
    data = read_instance(instance_filename)
    print(data['items'])
    print(data['nodes'])
    print(data['edges'])
    print(data['sources'])
    print(data['destinations'])

    # Générer le fichier .lp
    #lp_filename = f"{instance_filename.split('.')[0]}_{sys.argv[2]}.lp"
    #generate_lp_file(data, lp_filename, aggregated)
