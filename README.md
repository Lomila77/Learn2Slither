# Learn2Slither

Jeu Snake avec agent d'apprentissage par renforcement utilisant Q-Learning.

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Modifier le fichier `config.json` selon vos besoins :

```python
{
# Sauvegarde
    "save_as": "exploration",     # Nom de l'entrainement specifique
    "save_in": "./weights/exploration/",
    "load_data_from": "weights/force_exploration/10*10_epochs_40000_force_exploration_config.json",
    "load_weights_from": "weights/force_exploration/10*10_epochs_40000_force_exploration_weights.pck",
# Modes d'exécution
  # Si tout est faux passe en mode manuel
    "training_mode": true,        # True: entraînement, False: jeu
    "load_checkpoint": false,     # Charger un modèle pré-entraîné
    "ai_mode": false,             # True: IA joue, False: joueur humain
# Paramètres d'entraînement
    "map_shape": [40, 40],        # Taille de la grille
    "learning_rate": 0.9,         # Taux d'apprentissage
    "epsilon_greedy": 0.8,        # Exploration (0.0-1.0)
    "force_exploration": false,   # True: choix inconnue, False: choix random
    "epochs": 15000,              # Nombre d'époques
# Paramètres visuels
    "cell_size": 40,              # Taille des cellules
    "framerate": 60,              # FPS
    "speed": 150,                 # Vitesse de jeu (ms)
    "training_speed": 0           # Vitesse d'entraînement (ms)
}
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

- **Poids du modèle** : `.pck`
- **Information de l'entraînement** : `.json`
- **Graphiques de suivi** :
  - Objets collectés et taille du serpent par époque
  - Nombre de pas par époque

## Contrôles

- **Mode humain** : Flèches directionnelles ou WASD
- **Échap** : Quitter la partie
- **Mode IA** : Automatique
  - Appuyer sur n'importe quelles touches pour accelerer le rendue