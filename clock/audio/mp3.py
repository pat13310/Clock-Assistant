import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QUrl


class MP3Player:
    """
    Classe utilitaire pour lire des fichiers MP3 avec PySide6
    Utilise QMediaPlayer + QAudioOutput
    """

    def __init__(self, fichier: str):
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

        # Charger le fichier (chemin absolu recommandé)
        url = QUrl.fromLocalFile(fichier)
        self.player.setSource(url)

    def play(self):
        """Lance la lecture du MP3"""
        self.player.play()

    def pause(self):
        """Met en pause la lecture"""
        self.player.pause()

    def stop(self):
        """Arrête la lecture"""
        self.player.stop()

    def set_volume(self, valeur: int):
        """Ajuste le volume (0 à 100)"""
        self.audio_output.setVolume(valeur / 100.0)

    def is_playing(self) -> bool:
        """Retourne True si la lecture est en cours"""
        return self.player.playbackState() == QMediaPlayer.PlayingState
