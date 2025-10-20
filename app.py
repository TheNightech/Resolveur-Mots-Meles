
import os
import threading
from PIL import Image
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify
from pathlib import Path
import time # Nécessaire pour time.sleep()

# --- IMPORTS DIRECTS DU CODE DE TRAITEMENT ---
from python_part.main import run_processing_step # Importe la fonction modifiée

# --- Configuration ---
app = Flask(__name__)
UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) 
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

OUTPUT_DIR = os.path.join(UPLOAD_FOLDER, 'static', 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Supression des anciennes potentiels images
if Path("static/output/grid_output.png").exists():
    print("Ancienne image de grille de sortie suprimée")
    Path("static/output/grid_output.png").unlink()
if Path("grille.png").exists():
    print("Ancienne image de grille de entrée suprimée")
    Path("grille.png").unlink()
if Path("mots.png").exists():
    print("Ancienne image de liste de mots suprimée")
    Path("mots.png").unlink()

# --- Statut Global ---
PROCESS_STATUS = {
    'en_cours': False, 
    'mots_trouves': 0, 
    'total_mots': 0, 
    'last_update': 0, 
    'message': '',
    'final_status': None # 'done', 'error', 'finished'
}

# ----------------------------------------------------------------------
# FONCTIONS UTILITAIRES
# ----------------------------------------------------------------------

def convert_and_save(file_stream, target_filename):
    """Ouvre le flux de fichier et l'enregistre en PNG dans le répertoire racine."""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], target_filename)
    try:
        img = Image.open(file_stream)
        img.save(filepath, "PNG")
        return True
    except Exception as e:
        print(f"Erreur lors de la conversion et sauvegarde de {target_filename}: {e}")
        return False


def run_processing_loop():
    """
    Fonction lancée dans un thread pour gérer la boucle d'exécution de main.py
    jusqu'à la fin ou l'échec.
    """
    
    # Réinitialisation du statut avant le lancement
    PROCESS_STATUS.update({
        'en_cours': True, 
        'mots_trouves': 0, 
        'total_mots': 0, 
        'message': 'Initialisation...',
        'final_status': None
    })
    
    # Chemins des fichiers que run_processing_step attend
    img_path = Path("grille.png")
    img_mots = Path("mots.png")
    
    # Variables pour la boucle
    tentatives = 1
    mots_trouvés = 0
    status = 'continue'
    
    try:
        # Boucle tant que le traitement doit continuer (simule la récursion)
        while status == 'continue':
            
            print(f"\n[Thread] Lancement de l'étape {tentatives}")
            
            # Appel direct à la fonction de traitement
            result = run_processing_step(
                img_path, 
                img_mots, 
                tentatives=tentatives, 
                mots_trouvés=mots_trouvés
            )
            
            # Mise à jour du statut global basée sur le retour de run_processing_step
            mots_trouvés = result.get('mots_trouves', mots_trouvés)
            status = result['status']
            tentatives = result.get('tentatives', tentatives)
            total_mots = result.get('total_mots' , PROCESS_STATUS['total_mots']) # Utilise la valeur du statut s'il n'est pas fourni

            PROCESS_STATUS.update({
                'mots_trouves': mots_trouvés,
                'total_mots': total_mots,
                'last_update': int(datetime.now().timestamp()), 
                'message': f"Tentative #{tentatives} terminée. Statut: {status}"
            })
            
            # Si le statut n'est plus 'continue', on sort de la boucle
            if status != 'continue':
                PROCESS_STATUS['final_status'] = status
                break
                
            # Pause pour éviter une surcharge CPU trop rapide entre les tentatives
            time.sleep(1) 

        # Finalisation du processus
        if status == 'done':
            PROCESS_STATUS['message'] = "✅ Tous les mots ont été trouvés !"
        elif status == 'finished':
            PROCESS_STATUS['message'] = "Arrêt: Aucun mot supplémentaire trouvé."
        elif status == 'error':
            PROCESS_STATUS['message'] = f"❌ Erreur de traitement: {result.get('message', 'Erreur inconnue')}"

    except Exception as e:
        print(f"Erreur fatale dans le thread de traitement: {e}")
        PROCESS_STATUS['message'] = f"❌ Erreur fatale: {str(e)}"
        PROCESS_STATUS['final_status'] = 'error'

    finally:
        PROCESS_STATUS['en_cours'] = False
        print("--- Thread de traitement terminé ---")


# ----------------------------------------------------------------------
# ROUTES FLASK
# ----------------------------------------------------------------------

@app.context_processor
def inject_now():
    def now():
        return datetime.utcnow().strftime('%Y%m%d%H%M%S')
    return {'now': now}


@app.route('/')
def index():
    # Détermine si un résultat final est disponible pour l'affichage statique
    output_path = os.path.join(OUTPUT_DIR, 'grid_output.png')
    output_file_exists = os.path.exists(output_path) and not PROCESS_STATUS['en_cours']

    # Réinitialise le message s'il n'y a pas de statut en cours pour ne pas afficher le dernier message d'erreur/succès au rechargement initial
    message = PROCESS_STATUS['message'] if PROCESS_STATUS['message'] else None
    
    # Si le traitement est terminé, on efface le message pour l'affichage final statique
    if output_file_exists and PROCESS_STATUS['final_status'] in ['done', 'finished']:
        message = None
        
    return render_template(
        'index.html',
        status_check=PROCESS_STATUS['en_cours'],
        output_file_exists=output_file_exists,
        message=message
    )


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
                
    # Réinitialisation complète du statut
    PROCESS_STATUS.update({
        'en_cours': False, 'mots_trouves': 0, 'total_mots': 0, 
        'last_update': 0, 'message': 'Système réinitialisé.', 
        'final_status': None
    })
                
    return redirect(url_for('index'))


# app.py

# ... (autres imports et configurations) ...

# ... (autres routes) ...

@app.route('/relaunch')
def relaunch_processing():
    """
    Lance le traitement en utilisant les fichiers 'grille.png' et 'mots.png' 
    déjà sauvegardés, si un processus n'est pas déjà en cours.
    """
    
    if PROCESS_STATUS['en_cours']:
        return redirect(url_for('index', message="Un traitement est déjà en cours."))

    # Vérifiez que les fichiers existent
    GRID_PATH = os.path.join(app.config['UPLOAD_FOLDER'], 'grille.png')
    MOTS_PATH = os.path.join(app.config['UPLOAD_FOLDER'], 'mots.png')

    if not os.path.exists(GRID_PATH) or not os.path.exists(MOTS_PATH):
        # Si les fichiers n'existent plus, renvoyez l'utilisateur au formulaire
        return redirect(url_for('index', message="Erreur : Les fichiers précédents ont été supprimés. Veuillez recommencer l'upload."))
        
    # 1. Nettoyage de l'ancien fichier de sortie (comme dans /upload)
    output_path = os.path.join(OUTPUT_DIR, 'grid_output.png')
    if os.path.exists(output_path):
        os.remove(output_path)
        
    # 2. Lancement asynchrone (Thread)
    thread = threading.Thread(target=run_processing_loop)
    thread.start()
    
    # 3. Répondre immédiatement au client pour démarrer le polling JS
    return render_template(
        'index.html', 
        message="Relance du traitement en arrière-plan. Vérification de la progression en cours...", 
        status_check=True
    )
    
# ... (le reste du fichier app.py) ...

@app.route('/upload', methods=['POST'])
def upload_file():
    
    if PROCESS_STATUS['en_cours']:
        return redirect(url_for('index', message="Un traitement est déjà en cours. Veuillez attendre la fin."))
    
    if 'file_grille' not in request.files or 'file_mots' not in request.files:
        return redirect(url_for('index', message="Erreur : Les deux fichiers sont requis."))

    file_grille = request.files['file_grille']
    file_mots = request.files['file_mots']

    # 1. Nettoyage de l'ancien fichier de sortie (main.py le fera aussi, mais on s'assure qu'il est effacé immédiatement)
    output_path = os.path.join(OUTPUT_DIR, 'grid_output.png')
    if os.path.exists(output_path):
        os.remove(output_path)
        
    # 2. Renommage et Copie (dans le répertoire racine)
    success_grille = convert_and_save(file_grille, 'grille.png')
    success_mots = convert_and_save(file_mots, 'mots.png')

    if not success_grille or not success_mots:
        return redirect(url_for('index', message="Erreur lors de la conversion ou sauvegarde d'un des fichiers."))
        
    return redirect(url_for('relaunch_processing'))


@app.route('/status')
def check_status():
    """Route pour le polling JavaScript qui retourne l'état actuel du processus."""
    
    output_path = os.path.join(OUTPUT_DIR, 'grid_output.png')
    
    # Renvoyer l'état actuel et un horodatage pour forcer l'actualisation de l'image
    return jsonify({
        'en_cours': PROCESS_STATUS['en_cours'],
        'mots_trouves': PROCESS_STATUS['mots_trouves'],
        'total_mots': PROCESS_STATUS['total_mots'],
        'output_exists': os.path.exists(output_path),
        'timestamp': PROCESS_STATUS['last_update'],
        'final_status': PROCESS_STATUS['final_status'] # Nécessaire pour le contrôle JS
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)