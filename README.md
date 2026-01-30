# Learn2Slither

Jeu Snake avec agent d'apprentissage par renforcement utilisant Q-Learning.

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Modifier le fichier `config.py` selon vos besoins :

```python
# Modes d'exécution
TRAINING_MODE = False    # True: entraînement, False: jeu
AI_MODE = True          # True: IA joue, False: joueur humain
LOAD_CHECKPOINT = False # Charger un modèle pré-entraîné

# SI TOUT EST A FAUX PASSE EN MODE MANUEL

# Paramètres d'entraînement
MAP_SHAPE = [10, 10]    # Taille de la grille
LEARNING_RATE = 0.9     # Taux d'apprentissage
EPSILON_GREEDY = 0.0    # Exploration (0.0-1.0)
EPOCHS = 20000          # Nombre d'époques

# Paramètres visuels
CELL_SIZE = 40          # Taille des cellules
FRAMERATE = 60          # FPS
SPEED = 150            # Vitesse de jeu (ms)
TRAINING_SPEED = 0     # Vitesse d'entraînement (ms)

# Sauvegarde
FILENAME = "try_1"
DIRECTORY = "./weights/"
LOAD_WEIGHTS = "weights/10*10_epochs_40000_try_1_weights.pck"
LOAD_DATA = "weights/10*10_epochs_40000_try_1_config.json"
```

## Utilisation

### Lancer le jeu
```bash
python -m src.board
```

### Visualiser la Q-table
```bash
python -m src.utils
```

## Résultats

Après l'entraînement, les fichiers suivants sont générés dans `weights/` :

- **Poids du modèle** : `.pck` et `.json`
- **Graphiques de suivi** :
  - Objets collectés par époque
  - Nombre de pas par époque

## Contrôles

- **Mode humain** : Flèches directionnelles ou WASD
- **Échap** : Quitter la partie
- **Mode IA** : Automatique