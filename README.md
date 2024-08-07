# Projet : Transport Multi-Articles avec Nœuds Intermédiaires

## Description du Projet

Ce projet se concentre sur l'algorithmique et la recherche opérationnelle, plus précisément sur le problème de transport multi-articles avec nœuds intermédiaires. L'objectif est d'explorer les différences et de développer des méthodes efficaces pour résoudre ce problème complexe, tout en comparant deux approches : l'approche agrégée et l'approche désagrégée.

### Problématique

Le problème de transport de base implique le déplacement de marchandises entre des sources (producteurs) et des destinations (consommateurs) avec un objectif de minimiser les coûts de transport. Dans le cas du problème de transport multi-articles avec nœuds intermédiaires, des nœuds intermédiaires servent de points de transfert entre les sources et les destinations, augmentant ainsi la complexité. Les sources ne sont pas directement connectées aux destinations, et il peut y avoir plusieurs chemins entre une source et une destination.

Les objectifs sont :
1. Minimiser le coût de transport pour plusieurs types d’articles à travers des nœuds intermédiaires.
2. Comparer deux approches différentes :
   - **Approche Agrégée** : Considère les différents types d'articles comme une seule entité en sommant les capacités, les demandes et en prenant le coût médian.
   - **Approche Désagrégée** : Prend en compte les caractéristiques spécifiques de chaque type d'article pour une planification plus précise.

## Dépendances

Ce projet utilise les bibliothèques suivantes :
- **Pandas** (`^2.2.1`) : Pour la manipulation et l'analyse des données.
- **NetworkX** (`^3.2.1`) : Pour la création, la manipulation et l'étude des structures de graphes.
- **Matplotlib** (`^3.8.3`) : Pour la création de visualisations graphiques.

Vous pouvez installer ces dépendances en utilisant `pip` :

```bash
pip install pandas==2.2.1 networkx==3.2.1 matplotlib==3.8.3
```

## Utilisation

Pour générer le modèle, utilisez la commande suivante :

```bash
python3 generate_model <fichier_entree> <p>
```

- **`<fichier_entree>`** : Le fichier d'entrée contenant les données du problème.
- **`<p>`** : Paramètre déterminant le type de modèle à générer :
  - **`p = 0`** : Générer le modèle agrégé.
  - **`p = 1`** : Générer le modèle désagrégé.

### Exemples de Commandes

1. **Générer un modèle agrégé** :

   ```bash
   python3 generate_model 20_2_nonvalidly.txt 0
   ```

   Cette commande génère un fichier .lp pour le modèle agrégé à partir du fichier d'entrée.

2. **Générer un modèle désagrégé** :

   ```bash
   python3 generate_model 20_2_nonvalidly.txt 1
   ```

   Cette commande génère un fichier .lp pour le modèle désagrégé à partir du fichier d'entrée.

Pour résoudre le modèle généré, utilisez le solveur GLPK :

```bash
glpsol --lp <fichier_lp> -o <fichier_solution_output>
```

### Exemple de Résolution

Pour résoudre le modèle agrégé généré :

```bash
glpsol --lp 20_2_nonvalidly_0.lp -o 20_2_nonvalidly_0.sol
```

Pour résoudre le modèle désagrégé généré :

```bash
glpsol --lp 20_2_nonvalidly_1.lp -o 20_2_nonvalidly_1.sol
```
