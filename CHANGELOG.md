# Historique des versions - Clock Assistant

## Version init (Version initiale)
**Date de création :** Début du projet

### Fonctionnalités de base :
- **Affichage de l'heure** : Horloge numérique en temps réel avec format HH:MM:SS
- **Affichage de la date** : Date complète en français (jour, date, mois, année)
- **Saint du jour** : Affichage automatique du saint correspondant à la date
- **Interface personnalisée** : Fenêtre sans barre de titre standard avec cadre personnalisé
- **Dégradé de couleurs** : Changement automatique des couleurs selon l'heure de la journée
  - Matin : Tons dorés et orangés
  - Après-midi : Tons chauds
  - Soirée : Tons rosés et orangés
  - Nuit : Tons bleus foncés et noirs
- **Déplacement de fenêtre** : Possibilité de déplacer la fenêtre en cliquant-glissant
- **Bouton de fermeture** : Bouton rouge rond visible au survol de la souris
- **Configuration JSON** : Fichier de configuration pour personnaliser l'apparence

### Fichiers principaux :
- `clock/main.py` : Application principale
- `clock/config.json` : Configuration de l'interface
- `clock/saints.py` : Gestion des saints du jour

---

## Version 0.1 (Ajout des paramètres et météo)
**Fonctionnalités ajoutées :**

### Système de paramètres :
- **Boîte de dialogue des paramètres** : Interface pour modifier la configuration
- **Bouton paramètres** : Icône d'engrenage en haut à droite de l'horloge
- **Configuration en temps réel** : Modification des paramètres sans redémarrage
- **Sauvegarde automatique** : Les paramètres sont sauvegardés dans le fichier JSON

### Intégration météo :
- **API OpenWeatherMap** : Connexion à l'API météo pour récupérer les données
- **Barre météo** : Affichage de la température et conditions météorologiques
- **Rafraîchissement automatique** : Mise à jour périodique des données météo
- **Configuration météo** : Paramètres pour la ville et fréquence de mise à jour

### Améliorations interface :
- **Effets d'ombre** : Ombres portées sur les textes pour améliorer la lisibilité
- **Signature personnalisable** : Texte de signature configurable et masquable
- **Gestion des polices** : Configuration détaillée des polices pour chaque élément

### Fichiers ajoutés :
- `clock/settingsdialog.py` : Interface des paramètres
- `clock/openweather.py` : Gestion de l'API météo
- `test_weather_api.py` : Tests de l'API météo

---

## Version 0.2 (Système d'alarmes complet)
**Fonctionnalités ajoutées :**

### Système d'alarmes :
- **Gestionnaire d'alarmes** : Classe AlarmManager pour la gestion complète des alarmes
- **Bouton alarme** : Icône d'alarme en haut de l'horloge pour accéder aux paramètres
- **Interface de configuration** : Boîte de dialogue complète pour créer et gérer les alarmes
- **Sauvegarde JSON** : Persistance des alarmes dans un fichier `alarms.json`
- **Vérification périodique** : Timer qui vérifie chaque seconde si une alarme doit se déclencher

### Fonctionnalités d'alarme avancées :
- **Alarmes nommées** : Possibilité de donner un nom personnalisé à chaque alarme
- **Répétition par jours** : Sélection des jours de la semaine pour la répétition
- **Bouton "Tous"** : Sélection/désélection rapide de tous les jours
- **Sons personnalisables** : Choix parmi plusieurs fichiers audio disponibles
- **Messages personnalisés** : Texte optionnel affiché lors du déclenchement
- **Activation/désactivation** : Possibilité d'activer ou désactiver chaque alarme
- **Heure en temps réel** : Mise à jour automatique de l'heure actuelle dans le formulaire

### Notifications d'alarme :
- **Notifications visuelles** : Affichage d'une notification cliquable lors du déclenchement
- **Lecture audio** : Système de lecture des sons d'alarme avec QMediaPlayer
- **Arrêt par clic** : Possibilité d'arrêter l'alarme en cliquant sur la notification
- **Gestion des états** : Suivi de l'état de lecture des alarmes sonores

### Architecture améliorée :
- **BaseDialog** : Classe de base commune pour toutes les boîtes de dialogue
- **Marges centralisées** : Gestion unifiée des marges dans BaseDialog (40px gauche/droite, 40px haut, 20px bas)
- **Style uniforme** : Apparence cohérente pour toutes les interfaces
- **Boutons de fermeture** : Boutons rouges standardisés dans toutes les boîtes de dialogue
- **Coins arrondis** : Design moderne avec angles arrondis sur toutes les interfaces

### Fichiers ajoutés :
- `clock/alarmdialog.py` : Interface complète de gestion des alarmes
- `clock/basedialog.py` : Classe de base pour les boîtes de dialogue
- `clock/alarms.json` : Fichier de sauvegarde des alarmes
- `clock/assets/alarm.svg` : Icône du bouton alarme
- `clock/assets/close.svg` : Icône des boutons de fermeture
- Nombreux fichiers audio dans `clock/audio/` : Sons d'alarme variés

### Améliorations techniques :
- **Gestion des signaux** : Communication entre composants via le système de signaux Qt
- **Timer intelligent** : Optimisation des vérifications périodiques
- **Gestion mémoire** : Nettoyage approprié des ressources audio
- **Interface responsive** : Adaptation automatique de l'interface selon le contenu

---

## Évolution du projet

Le projet Clock Assistant a évolué d'une simple horloge numérique vers un assistant personnel complet avec :
- **Interface moderne** : Design soigné avec effets visuels
- **Fonctionnalités météo** : Intégration des données météorologiques
- **Système d'alarmes** : Gestion complète des rappels et alarmes
- **Configuration avancée** : Personnalisation poussée de tous les aspects
- **Architecture modulaire** : Code organisé et extensible pour de futures fonctionnalités
