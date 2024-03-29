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
    # Construction du modèle CPLEX LP agrégé
    model_str = ""
    # Ajoutez la construction du modèle ici
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
    print_data(data)

    # Générer le fichier .lp
    lp_filename =  f"{filename[:-4]}_{sys.argv[2]}.lp"
    save_model(data, lp_filename, aggregated)
    
