import pandas as pd
import sys

pd.set_option('display.precision', 16) # voir si possible de modif sur chaque x y 

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
