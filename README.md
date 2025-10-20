
🧩 Resolveur de Mots Mêlés (Word Search Solver)
Application web Flask utilisant le traitement d'image (via Pillow et des scripts de résolution personnalisés) pour trouver et surligner les mots cachés dans une grille à partir de deux images fournies par l'utilisateur.
Ce projet gère un processus de résolution potentiellement long en arrière-plan à l'aide de threads, avec un suivi de progression en temps réel (polling JavaScript) sur l'interface utilisateur.
🚀 Démarrage et Installation
Ces instructions vous guideront pour configurer et lancer le projet sur votre machine locale.
📋 Prérequis
Vous devez disposer de Python 3.x installé sur votre système.
1. Cloner le Dépôt
Ouvrez votre terminal et clonez le projet, puis naviguez dans le répertoire :
git clone https://github.com/TheNightech/Resolveur-Mots-Meles.git
cd Resolveur-Mots-Meles

2. Configuration de l'Environnement Virtuel (.venv)
Il est essentiel d'utiliser un environnement virtuel pour isoler les dépendances de votre projet.
# Créer l'environnement
python3 -m venv .venv

# Activer l'environnement (Linux/macOS)
source .venv/bin/activate

# Activer l'environnement (Windows PowerShell)
# .venv\Scripts\Activate.ps1

3. Installation des Dépendances
Installez toutes les librairies nécessaires (Flask, Pillow) à l'aide du fichier requirements.txt :
pip install -r requirements.txt

4. Créer un fichier .env pour mettre l'API key de votre IA pour openHosta.
Plus d'explications sur leur documentation:
https://github.com/hand-e-fr/OpenHosta

5. Lancer l'Application
Assurez-vous que l'environnement virtuel est toujours actif ((.venv) doit être visible dans votre terminal), puis lancez l'application Flask :
python app.py

L'application sera accessible via votre navigateur à l'adresse suivante : http://127.0.0.1:5000/
💡 Fonctionnalités Clés
 * Interface Web (Flask/Jinja) : Formulaire simple d'upload pour la grille et la liste des mots.
 * Traitement Asynchrone : La logique de résolution est exécutée dans un thread séparé (threading), empêchant l'interface utilisateur de se bloquer.
 * Suivi en Temps Réel (Polling) : Le JavaScript interroge régulièrement le serveur pour mettre à jour l'état de progression et l'image de sortie au fur et à mesure que les mots sont trouvés.
 * Résilience : Le bouton "Réessayer" relance le processus de résolution en utilisant les fichiers images déjà sauvegardés (grille.png et mots.png), sans nécessiter un nouvel upload.
 * Gestion des Erreurs : Affichage de messages clairs en cas d'erreur de format, de traitement, ou d'échec de la communication.
📁 Structure du Projet
Resolveur-Mots-Meles/
├── .venv/                      # Environnement virtuel (ignoré par Git)
├── .gitignore                  # Fichiers à ignorer (.venv, .env, images temporaires)
├── app.py                      # Application Flask : routes, gestion du statut, thread de lancement
├── main.py                     # Logique de traitement : appel aux fonctions de résolution, nettoyage, génération d'image
├── requirements.txt            # Liste des dépendances Python (Flask, Pillow)
├── templates/
│   └── index.html              # Interface utilisateur et logique JavaScript de Polling
└── static/
    └── style.css               # Styles CSS pour l'interface

🛑 Dépannage (Erreurs courantes)
| Problème | Cause la plus fréquente | Solution |
|---|---|---|
| ModuleNotFoundError: No module named 'Flask' | Environnement virtuel non actif ou dépendances non installées. | Activez le .venv (source .venv/bin/activate) puis exécutez pip install -r requirements.txt. |
| git push refusé (GH013) | Tentative de pousser un secret (clé API) dans l'historique Git. | Utilisez git reset --soft HEAD~1 pour annuler le commit, nettoyez le secret du fichier local (e.g., .env), puis faites un nouveau commit propre. |
| Le bouton "Réessayer" ne fait rien. | Les fichiers grille.png et mots.png n'ont pas été sauvegardés à la racine lors du premier upload. | Vérifiez les permissions du dossier et la logique de sauvegarde dans la route /upload de app.py. |
