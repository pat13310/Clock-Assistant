#!/usr/bin/env python3
"""
Script de démarrage pour l'horloge PySide6
"""

import sys
import os

def main():
    try:
        # Import et exécution de l'application
        from clock.main import Horloge
        from PySide6.QtWidgets import QApplication
        
        app = QApplication(sys.argv)
        horloge = Horloge()
        horloge.show()
        sys.exit(app.exec())
        
    except ImportError as e:
        print(f"Erreur d'import: {e}")
        print("Assurez-vous que l'environnement virtuel est activé et que les dépendances sont installées.")
        sys.exit(1)
    except Exception as e:
        print(f"Erreur lors du démarrage de l'application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()