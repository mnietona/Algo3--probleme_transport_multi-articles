import os
import subprocess
import sys
import platform

def create_venv():
    # Crée un environnement virtuel
    venv_dir = "env"
    if not os.path.exists(venv_dir):
        subprocess.run([sys.executable, "-m", "venv", venv_dir], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def install_dependencies():
    # Vérifie si le fichier requirements.txt existe
    if not os.path.exists("installation/requirements.txt"):
        return

    # Utilise le pip de l'environnement virtuel pour installer les dépendances
    venv_pip = os.path.join("env", "Scripts", "pip") if platform.system() == "Windows" else os.path.join("env", "bin", "pip")
    
    # Installer les dépendances
    subprocess.run([venv_pip, "install", "-r", "installation/requirements.txt"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    create_venv()
    install_dependencies()

if __name__ == "__main__":
    main()
