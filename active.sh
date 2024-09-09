#!/bin/bash

# Message de début d'exécution
echo "Préparation en cours... "

# Exécute le script Python
python3 installation/script.py

# Vérifie le système d'exploitation et active l'environnement virtuel
if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"* ]]; then
    source env/bin/activate
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    source env/Scripts/activate
else
    echo "Système d'exploitation non pris en charge pour l'activation de l'environnement virtuel."
    exit 1
fi

# Message de fin
echo "Tout est prêt. L'environnement virtuel est maintenant activé."