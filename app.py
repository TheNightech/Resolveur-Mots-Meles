# app.py

import os
import subprocess
import threading
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify
from PIL import Image

# --- Configuration ---
app = Flask(__name__)
# Le répertoire UPLOAD_FOLDER est le répertoire racine (où se trouvent app.py et main.py)
UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) 
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Le répertoire de sortie pour grid_output.png (dans static)
OUTPUT_DIR = os.path.join(UPLOAD_FOLDER, 'static', 'output')
# Assurez-vous que le répertoire static/output existe pour Flask
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Statut Global (Accessible par Flask et le Thread) ---
PROCESS_STATUS = {'en_cours': False, 'mots_trouves': 0, 'last_update': 0}


# ----------------------------------------------------------------------
# FONCTIONS UTILITAIRES
# ----------------------------------------------------------------------

def convert_and_save(file_stream, target_filename):
    """Ouvre le flux de fichier, le convertit/enregistre en PNG dans le répertoire racine."""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], target_filename)
    
    try:
        img = Image.open(file_stream)
        img.save(filepath, "PNG")
        return True
    except Exception as e:
        print(f"Erreur lors de la conversion et sauvegarde de {target_filename}: {e}")
        return False


def run_main_in_thread():
    """Fonction lancée dans un thread séparé pour exécuter main.py."""
    
    PROCESS_STATUS['en_cours'] = True
    PROCESS_STATUS['mots_trouves'] = 0
    
    print("\n--- Thread de main.py démarré ---")
    
    # Commande à exécuter (python3 python/main.py)
    command = ['python3', 'python/main.py']

    try:
        process = subprocess.Popen(
            command,
            cwd=app.config['UPLOAD_FOLDER'], 
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, 
            text=True,
            bufsize=1
        )
        
        # Lecture du flux en temps réel
        for line in process.stdout:
            
            print(f"[main.py] {line.strip()}")
            
            # Détection des mises à jour pour le client (polling)
            if "grid_output.png" in line or "Mots trouvés:" in line:
                PROCESS_STATUS['last_update'] = int(datetime.now().timestamp())
                
                # Extraction du nombre de mots trouvés (si le format est stable)
                if "Mots trouvés:" in line:
                     try:
                         # Exemple: "Mots trouvés: 15 / 20"
                         # Note: Le split doit être adapté si votre format de print change
                         found_str = line.split(':')[1].split('/')[0].strip()
                         PROCESS_STATUS['mots_trouves'] = int(found_str)
                     except Exception:
                         pass

        process.wait()
        
        # Finalisation
        if process.returncode == 0:
            print("Programme main.py terminé avec succès.")
            PROCESS_STATUS['mots_trouves'] = 'done'
        else:
            print(f"Le programme main.py a échoué (Code d'erreur {process.returncode}).")
            PROCESS_STATUS['mots_trouves'] = 'error'

    except Exception as e:
        print(f"Erreur lors de l'exécution du thread: {e}")
        PROCESS_STATUS['mots_trouves'] = 'error'

    finally:
        PROCESS_STATUS['en_cours'] = False
        print("--- Thread de main.py terminé ---")


# ----------------------------------------------------------------------
# ROUTES FLASK
# ----------------------------------------------------------------------

@app.context_processor
def inject_now():
    """Injecte l'heure pour le cache-busting (si non géré par timestamp/polling)."""
    def now():
        return datetime.utcnow().strftime('%Y%m%d%H%M%S')
    return {'now': now}


@app.route('/')
def index():
    """Affiche la page d'accueil."""
    return render_template('index.html')


@app.route('/restart')
def restart():
    """Supprime les anciens fichiers et redirige vers le formulaire."""
    
    # Chemins des fichiers à supprimer
    GRID_PATH = os.path.join(UPLOAD_FOLDER, 'grille.png')
    MOTS_PATH = os.path.join(UPLOAD_FOLDER, 'mots.png')
    OUTPUT_PATH = os.path.join(OUTPUT_DIR, 'grid_output.png')

    # Suppression des fichiers s'ils existent
    for path in [GRID_PATH, MOTS_PATH, OUTPUT_PATH]:
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception as e:
                print(f"Erreur lors de la suppression de {path}: {e}")
                
    # Réinitialisation du statut
    PROCESS_STATUS.update({'en_cours': False, 'mots_trouves': 0, 'last_update': 0})
                
    return redirect(url_for('index'))


@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Gère le téléchargement, la copie des fichiers, et lance l'exécution de main.py
    dans un thread séparé.
    """
    
    if PROCESS_STATUS['en_cours']:
        return render_template('index.html', message="Un traitement est déjà en cours. Veuillez attendre la fin.", output_file_exists=True)
    
    if 'file_grille' not in request.files or 'file_mots' not in request.files:
        return render_template('index.html', message="Erreur : Les deux fichiers sont requis.", output_file_exists=False)

    file_grille = request.files['file_grille']
    file_mots = request.files['file_mots']

    # 1. Nettoyage de l'ancien fichier de sortie
    output_path = os.path.join(OUTPUT_DIR, 'grid_output.png')
    if os.path.exists(output_path):
        os.remove(output_path)
        
    # 2. Renommage et Copie (dans le répertoire racine)
    success_grille = convert_and_save(file_grille, 'grille.png')
    success_mots = convert_and_save(file_mots, 'mots.png')

    if not success_grille or not success_mots:
        return render_template('index.html', message="Erreur lors de la conversion ou sauvegarde d'un des fichiers.", output_file_exists=False)
        
    
    # 3. Lancement asynchrone (Thread)
    thread = threading.Thread(target=run_main_in_thread)
    thread.start()
    
    # Répondre immédiatement au client pour démarrer le polling JS
    return render_template('index.html', message="Traitement lancé en arrière-plan. Vérification de la progression en cours...", status_check=True)


@app.route('/status')
def check_status():
    """Route pour le polling JavaScript qui retourne l'état actuel du processus."""
    
    output_path = os.path.join(OUTPUT_DIR, 'grid_output.png')
    
    # Renvoyer l'état actuel et un horodatage pour forcer l'actualisation de l'image
    return jsonify({
        'en_cours': PROCESS_STATUS['en_cours'],
        'mots_trouves': PROCESS_STATUS['mots_trouves'],
        'output_exists': os.path.exists(output_path),
        'timestamp': PROCESS_STATUS['last_update'] # Horodatage de la dernière mise à jour
    })


if __name__ == '__main__':
    # ATTENTION: Si vous utilisez Flask en mode debug (développement), le reloader peut 
    # lancer le thread deux fois. Pour la production, utilisez un serveur WSGI standard.
    app.run(debug=True, host='0.0.0.0', port=5000)