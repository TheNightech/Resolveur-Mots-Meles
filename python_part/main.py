from python_part.grid_to_text import image_of_char_grid_to_list_of_string
from python_part.list_to_text import image_of_list_of_words_to_list_of_string
from python_part.find_words import main as find_words_main
from PIL import Image
from PIL import ImageDraw, ImageFont
import unicodedata
from pathlib import Path

# NOTE: Le chemin de sortie est corrigé ici
OUTPUT_PATH = Path("static/output/grid_output.png")

# Renommée et modifiée pour être non récursive
def run_processing_step(img_path, img_mots, tentatives=1, mots_trouvés=0):

    # Lecture des images et conversion en listes de chaînes de caractères
    try:
        list_mots = image_of_list_of_words_to_list_of_string(Image.open(img_mots))
        img = Image.open(img_path)
        grid_list = image_of_char_grid_to_list_of_string(img)
    except FileNotFoundError:
        return {'status': 'error', 'message': "Les fichiers grille.png ou mots.png sont manquants."}
    except Exception as e:
        return {'status': 'error', 'message': f"Erreur de lecture d'image: {e}"}

    grid_list = clean_list(grid_list)
    list_mots = clean_list(list_mots)
    
    total_mots = len(list_mots)
    
    if grid_list and list_mots and verifi_grid(grid_list):
        print(f"Grille de taille {len(grid_list)} x {len(grid_list)} chargée.")
        print(f"{total_mots} mots à chercher chargés.") 
        
        # Recherche des mots
        answers = find_words_main(grid_list, list_mots)
        
        current_mots_trouvés = len(answers)
        
        if current_mots_trouvés <= mots_trouvés:
            print(f"Aucun mot supplémentaire trouvé. ({current_mots_trouvés} / {total_mots})")
            return {
                'status': 'continue', 
                'mots_trouves': mots_trouvés, 
                'total_mots': total_mots, 
                'tentatives': tentatives + 1
            }
        
        # Mots trouvés
        print(f"Mots trouvés: {current_mots_trouvés} / {total_mots}")
        
        make_new_grid(grid_list, answers).save("static/output/grid_output.png")
        print("grille créée")
        
        if current_mots_trouvés >= total_mots:
            print("Tous les mots ont été trouvés !")
            return {'status': 'done', 'mots_trouves': current_mots_trouvés, 'total_mots': total_mots}
        else:
            print("Certains mots n'ont pas été trouvés. Préparation de la prochaine tentative.")
            # Retourne le statut "continue" pour que app.py boucle
            return {
                'status': 'continue', 
                'mots_trouves': current_mots_trouvés, 
                'total_mots': total_mots, 
                'tentatives': tentatives + 1
            }
    else:
        return {
                'status': 'continue', 
                'mots_trouves': mots_trouvés, 
                'total_mots': total_mots, 
                'tentatives': tentatives + 1
            }
                
        
def clean_list(liste):
    # Nettoyer une liste de chaînes de caractères en supprimant les accents, en mettant en majuscules et en supprimant les espaces
    return [
        unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode('utf-8').upper().replace(" ", "")
        for s in liste
    ]

def verifi_grid(grid):
    # Vérifier la validité de la grille
    nb_lignes = len(grid)
    if nb_lignes == 0:
        return False
        
    is_valid = True
    for i in range(nb_lignes):
        if len(grid[i]) != nb_lignes:
            print(f"Erreure de l'IA ou mauvaise image ...\n Ligne {i + 1} a {len(grid[i])} caractères au lieu de {nb_lignes}.")
            is_valid = False

    return is_valid
 
def make_new_grid(grid, answers):
    # Créer une nouvelle image de la grille
    CELL_SIZE = 20
    img1 = Image.new('RGB', (len(grid)*CELL_SIZE, len(grid)*CELL_SIZE), color = (255, 255, 255))
    
    # Dessin des lettres
    for i, line in enumerate(grid):
        for j, char in enumerate(line):
            if char != " ":
                draw = ImageDraw.Draw(img1)
                try:
                    font = ImageFont.truetype("arial.ttf", 16)
                except IOError:
                    font = ImageFont.load_default()
                x, y = j * CELL_SIZE + 5, i * CELL_SIZE + 2
                draw.text((x, y), char, fill=(0, 0, 0), font=font)

    # Creer une copie de l'image 1 et dessiner les lignes des mots trouvés
    img2 = img1.copy()
    for ligne_start, col_start, ligne_end, col_end in answers:
        draw = ImageDraw.Draw(img2)
        # Ajustement des coordonnées pour centrer la ligne dans la cellule
        CENTER_OFFSET = CELL_SIZE / 2 + 0.5 
        
        start = ( col_start * CELL_SIZE - CENTER_OFFSET, ligne_start * CELL_SIZE - CENTER_OFFSET)
        end = ( col_end * CELL_SIZE - CENTER_OFFSET, ligne_end * CELL_SIZE - CENTER_OFFSET)
        draw.line([start, end], fill=(0, 200, 0), width=10)

    # Fusionner les deux images avec transparence
    img = Image.blend(img1, img2, alpha=0.6)
    return img