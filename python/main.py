
from grid_to_text import image_of_char_grid_to_list_of_string
from list_to_text import image_of_list_of_words_to_list_of_string
from find_words import main as find_words_main
from PIL import Image
from PIL import ImageDraw, ImageFont
import unicodedata
from pathlib import Path

# Fonction principale pour gérer le flux du programme
def main(img_path=None, img_mots=None, tentatives=1, mots_trouvés=0):

    # Suppression de l'ancienne image de sortie si elle existe
    if tentatives == 1:
        OUTPUT_PATH = Path("static/output/grid_output.png") # <-- Chemin Corrigé
        if OUTPUT_PATH.exists():
            print("Ancienne image suprimée")
            OUTPUT_PATH.unlink()
    # Obtention des chemins d'images si non fournis (première exécution)
    if img_path is None and img_mots is None:
        img_path = Path("grille.png")      
        img_mots = Path("mots.png")
        
        if not img_path.exists() or not img_mots.exists():
            print("ERREUR: Le fichier grille.png ou mots.png est manquant dans le répertoire racine.")
            return
        #     img_path = input("Chemin vers la grille de mots: ")
        # else:
        #     print("Image par défaut pour la grille de mots chargée.")
        # if not img_mots.exists():
        #     if input("(1 par défault): Donner une liste de mots à la main (1) ou en image (2): ") == "2":
        #         img_mots = input("Chemin vers l'image de la liste de mots: ")
        #     else:
        #         list_mots = input("Mots à chercher (séparés par des espaces): ").split() # .split() retourne une liste en utilisant les espaces comme séparateurs
        
        print("Image par défaut pour la liste de mots chargée.")
        print("Lancement de la tentative numéro 1.")
    # Lecture des images et conversion en listes de chaînes de caractères
    list_mots = image_of_list_of_words_to_list_of_string(Image.open(img_mots))
    img = Image.open(img_path)
    grid_list = image_of_char_grid_to_list_of_string(img)
    grid_list = clean_list(grid_list)
    list_mots = clean_list(list_mots)
    
    if grid_list and list_mots and verifi_grid(grid_list):
        print(f"Grille de taille {len(grid_list)} x {len(grid_list)} chargée.")
        print(f"{len(list_mots)} mots à chercher chargés.") 
        
        # Recherche des mots dans la grille à partir des listes fournies      
        answers = find_words_main(grid_list, list_mots)
        
        # Gestion des résultats de la recherche
        if len(answers) <= mots_trouvés:
            print("Aucun mot supplémentaire trouvé.")
            tentatives += 1
            print(f"lancement de la tentative numéro {tentatives}.")
            main(img_path, img_mots, tentatives, mots_trouvés)
            return
        
        print(f"Mots trouvés: {len(answers)} / {len(list_mots)}")
        make_new_grid(grid_list, answers).save("static/output/grid_output.png")
        
        if len(answers) >= len(list_mots):
            print("Tous les mots ont été trouvés !")
            print("Programme terminé. Résultat sauvegardé dans 'static/output/grid_output.png'.")
            return # Sortie propre, le code de retour sera 0 (succès)
        else:
            print("Certains mots n'ont pas été trouvés.")
            tentatives += 1
            mots_trouvés = len(answers)
            print(f"lancement de la tentative numéro {tentatives}.")
            main(img_path, img_mots, tentatives, mots_trouvés)
            return
    else:
        tentatives += 1
        print(f"Lancement de la tentative numéro {tentatives}.")
        main(img_path, img_mots, tentatives, mots_trouvés)
        return
        
def clean_list(liste):
    # Nettoyer une liste de chaînes de caractères en supprimant les accents, en mettant en majuscules et en supprimant les espaces
    return [
        unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode('utf-8').upper().replace(" ", "")
        for s in liste
    ]

def verifi_grid(grid):

    # Vérifier la validité de la grille
    nb_lignes = len(grid)
    for i in range(nb_lignes):
        if len(grid[i]) != nb_lignes:
            if len(grid[i]) > nb_lignes:
                print(f"Erreure lors de la lecture de la grille à la ligne {i + 1}. Trop de caractères.")
                print(f"Ligne {i + 1}: {grid[i]}")
            else:
                print(f"Erreure lors de la lecture de la grille à la ligne {i + 1}. Pas assez de caractères.")
                print(f"Ligne {i + 1}: {grid[i]}")
            return False

    return True
 
def make_new_grid(grid, answers):

    # Créer une nouvelle image de la grille
    img1 = Image.new('RGB', (len(grid)*20, len(grid)*20), color = (255, 255, 255))
    for i, line in enumerate(grid):
        for j, char in enumerate(line):
            if char != " ":
                draw = ImageDraw.Draw(img1)
                try:
                    font = ImageFont.truetype("arial.ttf", 16)
                except IOError:
                    font = ImageFont.load_default()
                x, y = j * 20 + 5, i * 20 + 2
                draw.text((x, y), char, fill=(0, 0, 0), font=font)

    # Creer une copie de l'image 1 et dessiner les lignes des mots trouvés
    img2 = img1.copy()
    for ligne_start, col_start, ligne_end, col_end in answers:
        draw = ImageDraw.Draw(img2)
        start = ( (col_start -1) * 20 + 7, (ligne_start -1) * 20 + 7)
        end = ( (col_end -1) * 20 + 7, (ligne_end -1) * 20 + 7)
        draw.line([start, end], fill=(0, 200, 0), width=10)

    # Fusionner les deux images avec transparence
    img = Image.blend(img1, img2, alpha=0.6)
    return img

if __name__ == "__main__":
    main()
    
