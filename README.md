# Learn2Slither

Jeu Snake avec agent d'apprentissage par renforcement utilisant Q-Learning.

## Installation

```bash
pip install -r requirements.txt
```

## Lancer le jeu

Vous pouvez lancer et configurer le jeu de 2 maniere differente, via le menu, ou via la CLI.

Afficher le menu avec la commande:
```bash
  python -m src.main    
```

Pour vous servir de la commande line vous pouvez afficher les options avec:
```bash
  python -m src.main --help
```

## Utilisation

### Visualiser la Q-table
```bash
python -m src.utils <q-table_path>
```

## Résultats

Après l'entraînement, les fichiers suivants sont générés dans `save/` :

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