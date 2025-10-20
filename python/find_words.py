def prepare_grid(grid, mots):

    nb_lignes = len(grid)
    # Enlever les espaces et les tabulations dans la grille
    for i in range(nb_lignes):
        grid[i] = grid[i].replace(" ", "").replace("\t", "")

    # Création des colonnes
    colonnes = []
    for i in range(nb_lignes):
        colonnes.append("")
        for l in range(len(grid[0])):
            colonnes[i] += grid[l][i]

    # Création des diagonales (de haut-gauche à bas-droite)
    diagonales_hg_bd = []
    # diagonales commençant sur la première colonne, du bas vers le haut (petites -> grandes)
    for i in range(nb_lignes - 1, -1, -1):
        diag = ""
        x, y = i, 0
        while x < nb_lignes and y < nb_lignes:
            diag += grid[x][y]
            x += 1
            y += 1
        diagonales_hg_bd.append(diag)

    # diagonales commençant sur la première ligne (sauf la première case), de gauche vers la droite (grandes -> petites)
    for j in range(1, nb_lignes):
        diag = ""
        x, y = 0, j
        while x < nb_lignes and y < nb_lignes:
            diag += grid[x][y]
            x += 1
            y += 1
        diagonales_hg_bd.append(diag)

    # Création des diagonales (de haut-droite à bas-gauche)
    diagonales_hd_bg = []
    # diagonales commençant sur la dernière colonne, du bas vers le haut (petites -> grandes)
    for i in range(nb_lignes - 1, -1, -1):
        diag = ""
        x, y = i, nb_lignes - 1
        while x < nb_lignes and y >= 0:
            diag += grid[x][y]
            x += 1
            y -= 1
        diagonales_hd_bg.append(diag)

    # diagonales commençant sur la première ligne (sauf la dernière case), de droite vers la gauche (grandes -> petites)
    for j in range(nb_lignes - 2, -1, -1):
        diag = ""
        x, y = 0, j
        while x < nb_lignes and y >= 0:
            diag += grid[x][y]
            x += 1
            y -= 1
        diagonales_hd_bg.append(diag)

    return colonnes, diagonales_hg_bd, diagonales_hd_bg

# Fonction pour chercher un mot à l'endroit
def chercher_mot_endroit(mot, grille, colonnes, diagonales_hg_bd, diagonales_hd_bg):
    answers = []
    # recherche du mot dans chaque ligne de la grille
    for ligne, contenu in enumerate(grille):
        if mot in contenu:
            print(f"Le mot {mot} a été trouvé à la ligne {ligne + 1}, colonne {contenu.index(mot) + 1} à colonne {contenu.index(mot) + len(mot)}.")
            answers.append((ligne + 1, contenu.index(mot) + 1, ligne + 1, contenu.index(mot) + len(mot)))

    # recherche du mot dans chaque colonne de la grille
    for colonne, contenu in enumerate(colonnes):
        if mot in contenu:
            print(f"Le mot {mot} a été trouvé à la colonne {colonne + 1}, ligne {contenu.index(mot) + 1} à ligne {contenu.index(mot) + len(mot)}.")
            answers.append((contenu.index(mot) + 1, colonne + 1, contenu.index(mot) + len(mot), colonne + 1))

    # diagonales HG-BD
    for diag, contenu in enumerate(diagonales_hg_bd):
        if mot in contenu:
            # Calcul des coordonnées de début et de fin
            index = contenu.index(mot) + 1
            if diag < len(grille):
                ligne_start = len(grille) - (diag - (index - 1))
                col_start = diag - (len(contenu) - index - 1)
            else:
                ligne_start = index
                col_start = len(grille) - (len(contenu) - index)
            ligne_end = ligne_start + (len(mot) - 1)
            col_end = col_start + (len(mot) - 1)
            answers.append((ligne_start, col_start, ligne_end, col_end))
            print(f"Le mot {mot} a été trouvé en diagonale HG-BD de la ligne {ligne_start}, colonne {col_start} à la ligne {ligne_end}, colonne {col_end}.")

    # diagonales HD-BG
    for diag, contenu in enumerate(diagonales_hd_bg):
        if mot in contenu:
            # Calcul des coordonnées de début et de fin
            index = contenu.index(mot) + 1
            if diag < len(grille):
                ligne_start = len(grille) - (diag - (index - 1))
                col_start = len(grille) - (index - 1)
            else:
                ligne_start = index
                col_start = len(contenu) - (index - 1)
            ligne_end = ligne_start + (len(mot) - 1)
            col_end = col_start - (len(mot) - 1)
            answers.append((ligne_start, col_start, ligne_end, col_end))
            print(f"Le mot {mot} a été trouvé en diagonale HD-BG de la ligne {ligne_start}, colonne {col_start} à la ligne {ligne_end}, colonne {col_end}.")

    return answers

# Fonction pour chercher un mot à l'envers
def chercher_mot_envers(mot, grille, colonnes, diagonales_hg_bd, diagonales_hd_bg):
    answers = []
    # recherche du mot dans chaque ligne de la grille
    for ligne, contenu in enumerate(grille):
        if mot in contenu:
            print(f"Le mot {mot[::-1]} a été trouvé à l'envers à la ligne {ligne + 1}, colonne {contenu.index(mot) + 1} à colonne {contenu.index(mot) + len(mot)}.")
            answers.append((ligne + 1, contenu.index(mot) + 1, ligne + 1, contenu.index(mot) + len(mot)))

    # recherche du mot dans chaque colonne de la grille
    for colonne, contenu in enumerate(colonnes):
        if mot in contenu:
            print(f"Le mot {mot[::-1]} a été trouvé à l'envers à la colonne {colonne + 1}, ligne {contenu.index(mot) + 1} à ligne {contenu.index(mot) + len(mot)}.")
            answers.append((contenu.index(mot) + 1, colonne + 1, contenu.index(mot) + len(mot), colonne + 1))

    # diagonales HG-BD
    for diag, contenu in enumerate(diagonales_hg_bd):
        if mot in contenu:
            # Calcul des coordonnées de début et de fin
            index = contenu.index(mot) + 1
            if diag < len(grille):
                ligne_start = len(grille) - (diag - (index - 1))
                col_start = diag - (len(contenu) - index - 1)
            else:
                ligne_start = index
                col_start = len(grille) - (len(contenu) - index)
            ligne_end = ligne_start + (len(mot) - 1)
            col_end = col_start + (len(mot) - 1)
            answers.append((ligne_start, col_start, ligne_end, col_end))
            print(f"Le mot {mot[::-1]} a été trouvé en diagonale HG-BD de la ligne {ligne_start}, colonne {col_start} à la ligne {ligne_end}, colonne {col_end}.")

    # diagonales HD-BG
    for diag, contenu in enumerate(diagonales_hd_bg):
        if mot in contenu:
            # Calcul des coordonnées de début et de fin
            index = contenu.index(mot) + 1
            if diag < len(grille):
                ligne_start = len(grille) - (diag - (index - 1))
                col_start = len(grille) - (index - 1)
            else:
                ligne_start = index
                col_start = len(contenu) - (index - 1)
            ligne_end = ligne_start + (len(mot) - 1)
            col_end = col_start - (len(mot) - 1)
            answers.append((ligne_start, col_start, ligne_end, col_end))
            print(f"Le mot {mot[::-1]} a été trouvé en diagonale HD-BG de la ligne {ligne_start}, colonne {col_start} à la ligne {ligne_end}, colonne {col_end}.")
    return answers

def main(grid, mots):

    colonnes, diagonales_hg_bd, diagonales_hd_bg = prepare_grid(grid, mots)
    answers = []

    # Chercher les mots à l'endroit
    for mot in mots:
        answers.extend(chercher_mot_endroit(mot, grid, colonnes, diagonales_hg_bd, diagonales_hd_bg))

    # Chercher les mots à l'envers
    for mot in mots:
        answers.extend(chercher_mot_envers(mot[::-1], grid, colonnes, diagonales_hg_bd, diagonales_hd_bg))

    return answers