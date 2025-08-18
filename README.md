# Horloge PySide6

Une application d'horloge numérique créée avec PySide6 (Qt pour Python).

## Fonctionnalités

- Affichage de l'heure en temps réel
- Affichage de la date en français
- Affichage du saint du jour en fonction de la date
- Dégradé de couleurs selon l'heure de la journée
- Interface sans barre de titre standard
- Cadre personnalisé avec dégradé gris sombre
- Possibilité de déplacer la fenêtre avec la souris
- Bouton rouge rond en haut à droite pour fermer l'application (visible uniquement au survol de la souris)
- Configuration personnalisable via un fichier de configuration

## Configuration de l'environnement

### Création de l'environnement virtuel

L'environnement virtuel a déjà été créé dans le dossier `venv`. Si vous devez le recréer :

```bash
python -m venv venv
```

### Activation de l'environnement virtuel

Sur Windows :
```bash
venv\Scripts\activate
```

Sur macOS/Linux :
```bash
source venv/bin/activate
```

### Installation des dépendances

Une fois l'environnement activé :

```bash
pip install -r requirements.txt
```

## Lancement de l'application

### Méthode 1 : Directement avec Python

```bash
python clock/main.py
```

### Méthode 2 : Via le script de démarrage

```bash
python run_clock.py
```

## Configuration

L'application peut être personnalisée via le fichier `clock/config.py` qui contient les paramètres suivants :

- Dimensions de la fenêtre
- Titre de la fenêtre
- Thèmes de couleurs selon l'heure de la journée
- Configuration du cadre personnalisé
- Polices et styles de texte
- Textes affichés

## Utilisation

- Cliquez et faites glisser n'importe où dans la fenêtre pour la déplacer
- L'heure, la date et le saint du jour sont mis à jour automatiquement chaque seconde
- Les couleurs de fond changent automatiquement selon l'heure de la journée
- Le bouton de fermeture rond en haut à droite n'est visible que lorsque vous passez la souris dessus

## Dépendances

- Python 3.7+
- PySide6

## Désactivation de l'environnement virtuel

```bash
deactivate