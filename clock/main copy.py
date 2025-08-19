import sys
import os
import datetime
import json
import random
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QPushButton,
    QHBoxLayout, QGraphicsDropShadowEffect, QGraphicsOpacityEffect,
    QGraphicsEffect, QDialog, QFormLayout, QLineEdit, QSpinBox, QDialogButtonBox, QCheckBox, QSizePolicy
)
from PySide6.QtCore import QTimer, Qt, QPoint, QPropertyAnimation, QEasingCurve, QObject, QParallelAnimationGroup, Property, QSize
from PySide6.QtGui import QFont, QPalette, QLinearGradient, QColor, QBrush, QPainter, QPen, QPolygonF, QIcon, QFontMetrics
from audio.mp3 import MP3Player

# Import de la configuration
from saints import SAINTS_DU_JOUR
from openweather import OpenWeather

# Fonction pour charger la configuration depuis le fichier JSON
def load_config():
    with open('clock/config.json', 'r') as f:
        return json.load(f)

# Charger la configuration
CONFIG = load_config()

# Extraire les variables de configuration
WINDOW_WIDTH = CONFIG["window"]["width"]
WINDOW_HEIGHT = CONFIG["window"]["height"]
WINDOW_TITLE = CONFIG["window"]["title"]
COLOR_THEMES = CONFIG["color_themes"]
FRAME_GRADIENT = CONFIG["frame_gradient"]
FONTS = CONFIG["fonts"]
TEXTS = CONFIG["texts"]

# Sauvegarde de la configuration dans le fichier JSON

def save_config(config):
    with open('clock/config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Paramètres")
        self.setWindowIcon(QIcon("clock/assets/settings.svg"))
        self.setModal(True)
        self._config = config
        # Style semblable à l'horloge
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumSize(420, 300)
        self.setStyleSheet("""
            QDialog, QWidget#DialogBackground { background: transparent; }
            QLabel { color: white; }
            QLineEdit, QSpinBox {
                background-color: rgba(0,0,0,120);
                color: white;
                border: 1px solid rgba(255,255,255,50);
                border-radius: 4px;
                padding: 2px 6px;
            }
            QCheckBox { color: white; }
            QDialogButtonBox QPushButton {
                background-color: #555;
                color: white;
                border-radius: 4px;
                padding: 4px 10px;
            }
            QDialogButtonBox QPushButton:hover { background-color: #666; }
        """)

        form = QFormLayout(self)
        form.setContentsMargins(20, 20, 20, 20)
        form.setSpacing(8)
        # Champs
        self.title_edit = QLineEdit(config["window"].get("title", ""))
        self.width_spin = QSpinBox()
        self.width_spin.setRange(200, 8000)
        self.width_spin.setValue(int(config["window"].get("width", 800)))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(200, 8000)
        self.height_spin.setValue(int(config["window"].get("height", 600)))
        self.signature_edit = QLineEdit(config.get("texts", {}).get("signature", ""))

        form.addRow("Titre", self.title_edit)
        form.addRow("Largeur", self.width_spin)
        form.addRow("Hauteur", self.height_spin)
        form.addRow("Signature", self.signature_edit)
        self.shadows_check = QCheckBox()
        self.shadows_check.setChecked(bool(config.get("effects", {}).get("shadows", True)))
        form.addRow("Ombre sur les textes", self.shadows_check)
        self.show_signature_check = QCheckBox()
        self.show_signature_check.setChecked(bool(config.get("display", {}).get("signature", True)))
        form.addRow("Afficher la signature", self.show_signature_check)
        # Rafraîchissement météo (minutes)
        self.weather_refresh_spin = QSpinBox()
        self.weather_refresh_spin.setRange(1, 180)
        self.weather_refresh_spin.setValue(int(config.get("weather", {}).get("refresh_minutes", 10)))
        form.addRow("Rafraîchissement météo (min)", self.weather_refresh_spin)
        # Affichage de la barre météo
        self.show_weather_bar_check = QCheckBox()
        self.show_weather_bar_check.setChecked(bool(config.get("display", {}).get("weather_bar", True)))
        form.addRow("Afficher la barre météo", self.show_weather_bar_check)
        if parent is not None and hasattr(parent, "preview_weather_bar_visibility"):
            self.show_weather_bar_check.toggled.connect(parent.preview_weather_bar_visibility)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Save).setText("Enregistrer")
        buttons.button(QDialogButtonBox.Cancel).setText("Annuler")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def values(self):
        return {
            "title": self.title_edit.text(),
            "width": int(self.width_spin.value()),
            "height": int(self.height_spin.value()),
            "signature": self.signature_edit.text(),
            "shadows": bool(self.shadows_check.isChecked()),
            "show_signature": bool(self.show_signature_check.isChecked()),
            "weather_refresh_minutes": int(self.weather_refresh_spin.value()),
            "show_weather_bar": bool(self.show_weather_bar_check.isChecked()),
        }

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        now = datetime.datetime.now()
        h = now.hour
        if 6 <= h < 12:
            start, end = COLOR_THEMES["morning"]["start"], COLOR_THEMES["morning"]["end"]
        elif 12 <= h < 18:
            start, end = COLOR_THEMES["afternoon"]["start"], COLOR_THEMES["afternoon"]["end"]
        elif 18 <= h < 21:
            start, end = COLOR_THEMES["evening"]["start"], COLOR_THEMES["evening"]["end"]
        else:
            start, end = COLOR_THEMES["night"]["start"], COLOR_THEMES["night"]["end"]

        rect_inner = self.rect().adjusted(6, 6, -6, -6)
        grad_inner = QLinearGradient(0, 0, 0, self.height())
        grad_inner.setColorAt(0, QColor(start))
        grad_inner.setColorAt(1, QColor(end))
        painter.setBrush(grad_inner)
        painter.setPen(QPen(QColor(30, 30, 30), 2))
        painter.drawRoundedRect(rect_inner, 10, 10)

        rect_ext = self.rect().adjusted(0, 0, -1, -1)
        grad_border = QLinearGradient(0, 0, 0, self.height())
        grad_border.setColorAt(0, QColor(FRAME_GRADIENT["start"]))
        grad_border.setColorAt(1, QColor(FRAME_GRADIENT["end"]))
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QBrush(grad_border), 25))
        painter.drawRoundedRect(rect_ext, 12, 12)


class ReliefLabel(QLabel):
    def paintEvent(self, event):
        # Dessin de base (fond + texte normal via style)
        super().paintEvent(event)
        # Dessin du relief: liseré blanc en haut-gauche et ombre noire en bas-droite
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = self.contentsRect()
        align = self.alignment()
        txt = self.text()
        # Highlight (haut-gauche)
        p.setPen(QPen(QColor(255, 255, 255, 200)))
        p.drawText(rect.translated(1, 1), align, txt)
        # Ombre (bas-droite)
        p.setPen(QPen(QColor(0, 0, 0, 150)))
        p.drawText(rect.translated(-1, -1), align, txt)


class Horloge(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Variables pour déplacement
        # Initialiser l'API OpenWeather
        self.openweather = OpenWeather("0c412981a35ed28fc18aac9ef4715ab9")  # Remplacer par une clé API valide
        self.drag_position = QPoint()
        # Cache des effets d'ombre pour éviter toute collecte
        self._text_shadows = {}

        # Layout principal
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(12, 8, 12, 2)

        # Heure
        self.label_heure = QLabel("--:--")
        self.label_heure.setAlignment(Qt.AlignCenter)
        font_heure = QFont(FONTS["time"]["family"], FONTS["time"]["size"])
        font_heure.setBold(FONTS["time"]["weight"] == "bold")
        self.label_heure.setFont(font_heure)

        # Secondes
        self.label_secondes = QLabel("--")
        self.label_secondes.setAlignment(Qt.AlignCenter)
        font_secondes = QFont(FONTS["time"]["family"], FONTS["time"]["size"] // 2)
        font_secondes.setBold(FONTS["time"]["weight"] == "bold")
        self.label_secondes.setFont(font_secondes)

        time_layout = QHBoxLayout()
        time_layout.setSpacing(4)
        time_layout.setAlignment(Qt.AlignCenter)
        time_layout.addStretch(1)
        time_layout.addWidget(self.label_heure, 0, Qt.AlignVCenter)
        time_layout.addWidget(self.label_secondes, 0, Qt.AlignVCenter)
        time_layout.addStretch(1)
        
        # Date
        self.label_date = QLabel("")
        self.label_date.setAlignment(Qt.AlignCenter)
        font_date = QFont(FONTS["date"]["family"], FONTS["date"]["size"])
        self.label_date.setFont(font_date)
        # Garantir aucune troncature: hauteur minimale = métriques de police
        fm_date_h = QFontMetrics(font_date).height()
        self.label_date.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.label_date.setMinimumHeight(fm_date_h + 2)
        # Conteneur pour figer la hauteur de la zone date
        self.date_container = QWidget()
        self.date_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.date_container.setFixedHeight(fm_date_h + 4)
        _date_layout = QHBoxLayout(self.date_container)
        _date_layout.setContentsMargins(0, 0, 0, 0)
        _date_layout.setSpacing(0)
        _date_layout.addStretch(1)
        _date_layout.addWidget(self.label_date)
        _date_layout.addStretch(1)

        # Fête du jour
        self.label_fete = QLabel(TEXTS["holiday"])
        self.label_fete.setAlignment(Qt.AlignCenter)
        font_fete = QFont(FONTS["holiday"]["family"], FONTS["holiday"]["size"])
        font_fete.setItalic(FONTS["holiday"]["italic"])
        self.label_fete.setFont(font_fete)
        self.label_fete.setStyleSheet("color: #f2f2f2;")
        # Garantir aucune troncature: hauteur minimale = métriques de police
        fm_fete_h = QFontMetrics(font_fete).height()
        self.label_fete.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.label_fete.setMinimumHeight(fm_fete_h + 2)
        # Conteneur pour figer la hauteur de la zone saint
        self.fete_container = QWidget()
        self.fete_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.fete_container.setFixedHeight(fm_fete_h + 4)
        _fete_layout = QHBoxLayout(self.fete_container)
        _fete_layout.setContentsMargins(0, 0, 0, 0)
        _fete_layout.setSpacing(0)
        _fete_layout.addStretch(1)
        _fete_layout.addWidget(self.label_fete)
        _fete_layout.addStretch(1)
        
        # Infos météo (pression + vent)
        self.label_meteo_info = QLabel("")
        self.label_meteo_info.setAlignment(Qt.AlignCenter)
        font_meteo = QFont(FONTS["date"]["family"], max(8, FONTS["date"]["size"] - 2))
        self.label_meteo_info.setFont(font_meteo)
        self.label_meteo_info.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        #self.label_meteo_info.setMaximumWidth(int(WINDOW_WIDTH * 0.98))
        self.label_meteo_info.setStyleSheet("font-weight: bold;background-color: rgba(255,255,255,70); color: #222; padding: 2px 12px; font-size: 11px; border-radius: 8px; border: 1px solid rgba(0,0,0,0.2);margin-top: 28px;")

        # Message temporaire (overlay)
        self.overlay_message = QLabel("", self)
        self.overlay_message.setAlignment(Qt.AlignCenter)
        self.overlay_message.setStyleSheet("""
            QLabel {
                background-color: rgba(0,0,0,150);
                color: white;
                border-radius: 8px;
                padding: 5px 10px;
                font-size: 10px;
            }
        """)
        self.overlay_message.hide()

        # Signature
        self.label_signature = QLabel(TEXTS["signature"], self)
        self.label_signature.setFont(QFont(FONTS["signature"]["family"], FONTS["signature"]["size"]))
        self.label_signature.setStyleSheet(f"color: {FONTS['signature']['color']};")
        self.label_signature.adjustSize()
        self.label_signature.move(WINDOW_WIDTH - self.label_signature.width() - 10,
                                  WINDOW_HEIGHT - self.label_signature.height() - 10)

        # Conteneur pour stabiliser la hauteur de la ligne heure+secondes
        fm_h = QFontMetrics(font_heure).height()
        fm_s = QFontMetrics(font_secondes).height()
        container_h = max(fm_h, fm_s) + 2
        self.time_container = QWidget()
        self.time_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.time_container.setFixedHeight(container_h)
        self.time_container.setLayout(time_layout)
        layout.addWidget(self.time_container)
        layout.addWidget(self.date_container)
        layout.addWidget(self.fete_container)
        layout.addStretch()
        layout.addWidget(self.label_meteo_info, 0, Qt.AlignHCenter | Qt.AlignBottom)
        self.setLayout(layout)

        # Bouton fermeture (icône SVG au lieu de la croix)
        self.close_button = QPushButton("", self)
        self.close_button.setIcon(QIcon("clock/assets/close.svg"))
        self.close_button.setIconSize(QSize(12, 12))
        self.close_button.setFixedSize(16, 16)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: red;
                border-radius: 8px;
                padding: 0;
            }
            QPushButton:hover { background-color: #cc0000; }
        """)
        self.close_button.setToolTip("Fermer")
        self.close_button.move(WINDOW_WIDTH - 25, 2)
        self.close_button.clicked.connect(self.close)

        # Bouton paramètres (icône SVG)
        self.settings_button = QPushButton("", self)
        self.settings_button.setIcon(QIcon("clock/assets/settings.svg"))
        self.settings_button.setIconSize(QSize(18, 18))
        self.settings_button.setFixedSize(18, 18)
        self.settings_button.setStyleSheet("""
            QPushButton {
                background-color: #555;
                border-radius: 9px;
                padding: 0;
            }
            QPushButton:hover { background-color: #333; }
        """)
        self.settings_button.setToolTip("Paramètres")
        self.settings_button.move(WINDOW_WIDTH - 25 - 24, 2)
        self.settings_button.clicked.connect(self.open_settings)
        # Appliquer la configuration initiale (dont visibilité de la signature)
        self.apply_config_to_ui()

        # Sons
        base_dir = os.path.dirname(os.path.abspath(__file__))
        tick_path = os.path.join(base_dir, "audio", "tick.mp3")
        chime_path = os.path.join(base_dir, "audio", "chime.mp3")
        self.tick_sound = MP3Player(tick_path)
        self.period_sound = MP3Player(chime_path)
        self.tick_sound.set_volume(50)
        self.period_sound.set_volume(50)

        # Ombres sur les textes selon configuration
        self.apply_or_remove_text_shadows()

        # Timers
        self.update_time()
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)

        # Timer météo pour mettre à jour la bande noire périodiquement
        self.weather_timer = QTimer(self)
        self.weather_timer.timeout.connect(self.update_weather_info)
        minutes = int(CONFIG.get("weather", {}).get("refresh_minutes", 10))
        self.weather_timer.start(minutes * 60 * 1000)  # minutes paramétrables
        # Premier rafraîchissement immédiat
        self.update_weather_info()
        # Appliquer la config (pour éventuellement cacher la barre et arrêter le timer)
        self.apply_config_to_ui()

        # Signature auto fade
        QTimer.singleShot(5000, self.start_fade_out)

    def apply_text_shadow(self, label):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(3)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 200))
        label.setGraphicsEffect(shadow)
        # Conserver une référence
        self._text_shadows[label] = shadow

    def start_fade_out(self):
        self.opacity_effect = QGraphicsOpacityEffect()
        self.label_signature.setGraphicsEffect(self.opacity_effect)
        anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        anim.setDuration(2000)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.start()

    def apply_or_remove_text_shadows(self):
        labels = [self.label_heure, self.label_secondes, self.label_date, self.label_fete]
        enabled = bool(CONFIG.get("effects", {}).get("shadows", True))
        for lbl in labels:
            # Nettoyer l'effet courant
            lbl.setGraphicsEffect(None)
            if enabled:
                self.apply_text_shadow(lbl)
            else:
                # Supprimer la référence si existante
                if hasattr(self, "_text_shadows") and lbl in self._text_shadows:
                    try:
                        del self._text_shadows[lbl]
                    except Exception:
                        pass
            lbl.update()
        # Effet relief assuré par ReliefLabel (pas de QGraphicsEffect ici)
        if hasattr(self, 'label_meteo_info'):
            self.label_meteo_info.setGraphicsEffect(None)
            self.label_meteo_info.update()

    def apply_config_to_ui(self):
        """Applique la configuration en cours à l'interface (titre, taille, signature, positions)."""
        w = int(CONFIG["window"]["width"])  # largeur
        h = int(CONFIG["window"]["height"])  # hauteur
        self.setWindowTitle(CONFIG["window"]["title"])  # titre
        self.setFixedSize(w, h)
        # Signature
        self.label_signature.setText(CONFIG["texts"].get("signature", ""))
        self.label_signature.adjustSize()
        self.label_signature.move(w - self.label_signature.width() - 10,
                                  h - self.label_signature.height() - 1)
        # Recalibrer la hauteur du conteneur heure+secondes
        try:
            fm_h = QFontMetrics(self.label_heure.font()).height()
            fm_s = QFontMetrics(self.label_secondes.font()).height()
            container_h = max(fm_h, fm_s) + 2
            if hasattr(self, 'time_container'):
                self.time_container.setFixedHeight(container_h)
            # Recalibrer aussi les hauteurs minimales pour la date et la fête du jour
            fm_date_h = QFontMetrics(self.label_date.font()).height()
            self.label_date.setMinimumHeight(fm_date_h + 2)
            if hasattr(self, 'date_container'):
                self.date_container.setFixedHeight(fm_date_h + 4)
            fm_fete_h = QFontMetrics(self.label_fete.font()).height()
            self.label_fete.setMinimumHeight(fm_fete_h + 2)
            if hasattr(self, 'fete_container'):
                self.fete_container.setFixedHeight(fm_fete_h + 4)
        except Exception:
            pass
        # Affichage/masquage de la signature et de la barre météo
        show_sig = bool(CONFIG.get("display", {}).get("signature", True))
        show_bar = bool(CONFIG.get("display", {}).get("weather_bar", True))
        # Si la barre météo est visible et la signature activée, on évite le doublon en cachant le label dédié
        if show_bar and show_sig:
            self.label_signature.hide()
        else:
            if show_sig:
                self.label_signature.show()
            else:
                self.label_signature.hide()
        if hasattr(self, 'label_meteo_info'):
            self.label_meteo_info.setMaximumWidth(int(w * 0.9))
            if show_bar:
                # Mettre à jour le contenu avant l'animation pour une taille correcte
                self.update_weather_info()
                self.animate_weather_bar_visibility(True)
            else:
                self.animate_weather_bar_visibility(False)
            lay = self.layout()
            if lay is not None:
                lay.activate()
        # Boutons
        self.close_button.move(w - 25, 2)
        if hasattr(self, 'settings_button'):
            self.settings_button.move(w - 25 - 24, 2)
        # Ombre portée
        self.apply_or_remove_text_shadows()
        # Redémarrer/arrêter le timer météo selon l'affichage de la barre
        if hasattr(self, 'weather_timer'):
            minutes = int(CONFIG.get("weather", {}).get("refresh_minutes", 10))
            show_bar = bool(CONFIG.get("display", {}).get("weather_bar", True))
            if show_bar:
                self.weather_timer.start(minutes * 60 * 1000)
                self.update_weather_info()
            else:
                self.weather_timer.stop()
        # Rafraîchir palette/cadres
        self.rafraichir_zone_horloge()
        self.update()

    def rafraichir_zone_horloge(self):
        """Rafraîchit la zone contenant l'heure, la date et la fête du jour."""
        try:
            for lbl in (self.label_heure, self.label_secondes, self.label_date, self.label_fete):
                lbl.adjustSize()
                lbl.update()
            lay = self.layout()
            if lay is not None:
                lay.activate()
        except Exception:
            pass

    
    def animate_weather_bar_visibility(self, show):
        """Anime proprement l'apparition/disparition de la barre météo sans casser le layout."""
        if not hasattr(self, 'label_meteo_info'):
            return
        lbl = self.label_meteo_info
        try:
            # Stopper une éventuelle animation précédente
            if hasattr(self, '_meteo_anim') and self._meteo_anim is not None:
                try:
                    self._meteo_anim.stop()
                except Exception:
                    pass
            start_h = max(0, int(lbl.maximumHeight()))
            if show:
                target_h = max(1, int(lbl.sizeHint().height()))
                lbl.setMaximumHeight(start_h)
                lbl.show()
                self._meteo_anim = QPropertyAnimation(lbl, b"maximumHeight", self)
                self._meteo_anim.setDuration(250)
                self._meteo_anim.setStartValue(start_h)
                self._meteo_anim.setEndValue(target_h)
                self._meteo_anim.setEasingCurve(QEasingCurve.InOutQuad)
                self._meteo_anim.start()
            else:
                self._meteo_anim = QPropertyAnimation(lbl, b"maximumHeight", self)
                self._meteo_anim.setDuration(250)
                self._meteo_anim.setStartValue(start_h if start_h > 0 else int(lbl.sizeHint().height()))
                self._meteo_anim.setEndValue(0)
                self._meteo_anim.setEasingCurve(QEasingCurve.InOutQuad)
                def _after_hide():
                    try:
                        lbl.hide()
                        lbl.clear()
                    except Exception:
                        pass
                self._meteo_anim.finished.connect(_after_hide)
                self._meteo_anim.start()
        except Exception:
            # Fallback
            if show:
                lbl.setMaximumHeight(16777215)
                lbl.show()
            else:
                lbl.setMaximumHeight(0)
                try:
                    lbl.hide()
                    lbl.clear()
                except Exception:
                    pass
        finally:
            lay = self.layout()
            if lay is not None:
                lay.activate()

    def preview_weather_bar_visibility(self, visible):
        """Aperçu immédiat de la visibilité de la barre météo depuis la boîte de dialogue de paramètres.
        Gère aussi la signature pour éviter les doublons et corriger l'affichage.
        """
        if not hasattr(self, "label_meteo_info"):
            return

        show_bar = bool(visible)
        # Afficher/masquer la barre météo immédiatement
        if show_bar:
            # Éviter le doublon: si la signature est activée dans la config, on la cache quand la barre est visible
            if bool(CONFIG.get("display", {}).get("signature", True)) and hasattr(self, "label_signature"):
                self.label_signature.hide()
            # Relancer le timer et rafraîchir les infos
            if hasattr(self, "weather_timer"):
                minutes = int(CONFIG.get("weather", {}).get("refresh_minutes", 10))
                self.weather_timer.start(minutes * 60 * 1000)
            self.update_weather_info()
            self.animate_weather_bar_visibility(True)
        else:
            # Stopper le timer
            if hasattr(self, "weather_timer"):
                self.weather_timer.stop()
            self.animate_weather_bar_visibility(False)
            # Comme la barre n'est plus visible, si la signature est activée dans la config on la ré-affiche
            if bool(CONFIG.get("display", {}).get("signature", True)) and hasattr(self, "label_signature"):
                self.label_signature.show()
        # Forcer un recalcul/rafraîchissement de la mise en page
        lay = self.layout()
        if lay is not None:
            lay.activate()
        self.rafraichir_zone_horloge()
        self.update()

    def open_settings(self):
        dlg = SettingsDialog(CONFIG, self)
        result = dlg.exec()
        if result:
            vals = dlg.values()
            # Mettre à jour le modèle de config
            CONFIG["window"]["title"] = vals["title"]
            CONFIG["window"]["width"] = vals["width"]
            CONFIG["window"]["height"] = vals["height"]
            CONFIG.setdefault("texts", {})["signature"] = vals["signature"]
            CONFIG.setdefault("effects", {})["shadows"] = vals["shadows"]
            CONFIG.setdefault("display", {})["signature"] = vals["show_signature"]
            CONFIG.setdefault("display", {})["weather_bar"] = vals["show_weather_bar"]
            CONFIG.setdefault("weather", {})["refresh_minutes"] = vals["weather_refresh_minutes"]
            # Sauvegarde sur disque
            save_config(CONFIG)
            # Appliquer directement
            self.apply_config_to_ui()
        else:
            # Annulé: rétablir l'interface
            self.apply_config_to_ui()

    def show_overlay_message(self, text):
        # Positionner et afficher le message
        self.overlay_message.setText(text)
        self.overlay_message.adjustSize()
        self.overlay_message.move(
            (self.width() - self.overlay_message.width()) // 2,
            self.height() - self.overlay_message.height() - 2
        )
        self.overlay_message.show()

        # Arrêter une animation précédente si nécessaire
        if hasattr(self, "_overlay_anim") and self._overlay_anim is not None:
            try:
                self._overlay_anim.stop()
            except Exception:
                pass

        # Créer (ou réutiliser) l'effet d'opacité et le conserver
        if not hasattr(self, "_overlay_effect") or self._overlay_effect is None:
            self._overlay_effect = QGraphicsOpacityEffect(self.overlay_message)
        self.overlay_message.setGraphicsEffect(self._overlay_effect)
        self._overlay_effect.setOpacity(1.0)

        # Créer l'animation et la conserver pour éviter la collecte
        self._overlay_anim = QPropertyAnimation(self._overlay_effect, b"opacity", self)
        self._overlay_anim.setDuration(3000)
        self._overlay_anim.setStartValue(1.0)
        self._overlay_anim.setEndValue(0.0)
        self._overlay_anim.setEasingCurve(QEasingCurve.InOutQuad)
        self._overlay_anim.finished.connect(self.overlay_message.hide)
        self._overlay_anim.start()

    def update_weather_info(self):
        """Met à jour la ligne d'infos en bas (Température, Humidité, Pression, Vent) et affiche un message météo."""
        # Si la barre météo est désactivée, masquer et vider immédiatement
        if not bool(CONFIG.get("display", {}).get("weather_bar", True)):
            if hasattr(self, "label_meteo_info"):
                #self.label_meteo_info.clear()
                self.label_meteo_info.hide()
            return
        weather_data = self.openweather.get_weather_data()
        if weather_data:
            condition = self.openweather.get_weather_condition(weather_data)
            temperature = weather_data["main"]["temp"]
            humidity = weather_data.get("main", {}).get("humidity")
            description = weather_data["weather"][0]["description"]
            # Récupérer les autres infos et construire un message temporaire enrichi
            pressure = weather_data.get("main", {}).get("pressure")
            wind = weather_data.get("wind", {})
            speed_ms = wind.get("speed")
            deg = wind.get("deg")
            msg_parts = [f"Météo: {description}"]
            try:
                msg_parts.append(f"Température: {float(temperature):.0f}°C")
            except Exception:
                pass
            if humidity is not None:
                msg_parts.append(f"Humidité: {humidity}%")
            if pressure is not None:
                msg_parts.append(f"Pression: {pressure} hPa")
            if speed_ms is not None:
                try:
                    speed_kmh_msg = round(float(speed_ms) * 3.6)
                except Exception:
                    speed_kmh_msg = None
                direction_msg = self._wind_direction(deg)
                if speed_kmh_msg is not None:
                    if direction_msg:
                        msg_parts.append(f"Vent: {speed_kmh_msg} km/h ({direction_msg})")
                    else:
                        msg_parts.append(f"Vent: {speed_kmh_msg} km/h")
            weather_message = " • ".join(msg_parts)
            # self.show_overlay_message(weather_message)  # Désactivé pour éviter une seconde barre
            # Construire la ligne
            pressure = weather_data.get("main", {}).get("pressure")
            wind = weather_data.get("wind", {})
            speed_ms = wind.get("speed")
            deg = wind.get("deg")
            parts = []
            if temperature is not None:
                try:
                    temp_val = float(temperature)
                    parts.append(f"Température: {temp_val:.0f}°C")
                except Exception:
                    pass
            if humidity is not None:
                parts.append(f"Humidité: {humidity}%")
            if pressure is not None:
                parts.append(f"Pression: {pressure} hPa")
            if speed_ms is not None:
                try:
                    speed_kmh = round(float(speed_ms) * 3.6)
                except Exception:
                    speed_kmh = None
                direction = self._wind_direction(deg)
                if speed_kmh is not None:
                    if direction:
                        parts.append(f"Vent: {speed_kmh} km/h ({direction})")
                    else:
                        parts.append(f"Vent: {speed_kmh} km/h")
            # Ajouter la signature en fin de barre si activée
            if bool(CONFIG.get("display", {}).get("signature", True)):
                sig_text = CONFIG.get("texts", {}).get("signature", "")
                if sig_text:
                    parts.append(sig_text)
            if hasattr(self, "label_meteo_info"):
                self.label_meteo_info.setText(" • ".join(parts))
            # Animation météo
            self.apply_weather_animation(condition)
        else:
            # Pas de données météo
            if hasattr(self, "label_meteo_info"):
                self.label_meteo_info.setText("Météo indisponible")

    
    def apply_weather_animation(self, condition):
        """
        Applique une animation en fonction de la condition météo.
        """
        # Réinitialiser les animations précédentes
        if hasattr(self, '_weather_animation_group'):
            self._weather_animation_group.stop()
        
        # Créer un groupe d'animations
        self._weather_animation_group = QParallelAnimationGroup()
        
        # Appliquer une animation différente selon la condition
        if condition == "rain":
            self._apply_rain_animation()
        elif condition == "snow":
            self._apply_snow_animation()
        elif condition == "storm":
            self._apply_storm_animation()
        elif condition == "clear":
            self._apply_clear_animation()
        elif condition == "partially_cloudy":
            self._apply_partially_cloudy_animation()
        elif condition == "clouds":
            self._apply_clouds_animation()
        else:
            # Par défaut, pas d'animation spéciale
            pass
    
    def _apply_rain_animation(self):
        """
        Applique une animation de pluie.
        """
        # Pour l'instant, on change simplement la couleur de fond
        # Dans une implémentation plus avancée, on pourrait ajouter des particules
        self._apply_background_animation("#4a90e2", "#2c5aa0")  # Bleu pour la pluie
    
    def _apply_snow_animation(self):
        """
        Applique une animation de neige.
        """
        # Pour l'instant, on change simplement la couleur de fond
        self._apply_background_animation("#e0f0ff", "#a0c0e0")  # Bleu clair pour la neige
    
    def _apply_storm_animation(self):
        """
        Applique une animation d'orage.
        """
        # Pour l'instant, on change simplement la couleur de fond
        self._apply_background_animation("#303030", "#101010")  # Gris foncé pour l'orage
    
    def _apply_clear_animation(self):
        """
        Applique une animation de ciel dégagé.
        """
        # Pour l'instant, on change simplement la couleur de fond
        self._apply_background_animation("#87ceeb", "#f0e68c")  # Bleu ciel pour le soleil
    
    def _apply_partially_cloudy_animation(self):
        """
        Applique une animation de ciel partiellement nuageux.
        """
        # Pour l'instant, on change simplement la couleur de fond
        self._apply_background_animation("#b0c4de", "#708090")  # Bleu gris pour les nuages
    
    def _apply_clouds_animation(self):
        """
        Applique une animation de ciel nuageux.
        """
        # Pour l'instant, on change simplement la couleur de fond
        self._apply_background_animation("#708090", "#2f4f4f")  # Gris pour les nuages
    
    def _wind_direction(self, deg):
        """Retourne la direction du vent en abréviation française (N, NNE, NE, ENE, E, ESE, SE, SSE, S, SSO, SO, OSO, O, ONO, NO, NNO)."""
        if deg is None:
            return None
        dirs = ["N","NNE","NE","ENE","E","ESE","SE","SSE","S","SSO","SO","OSO","O","ONO","NO","NNO"]
        idx = int((deg % 360) / 22.5 + 0.5) % 16
        return dirs[idx]
    
    def _apply_background_animation(self, start_color, end_color):
        """
        Applique une animation de changement de couleur de fond.
        """
        # Créer une animation pour le dégradé de fond
        start_anim = QPropertyAnimation(self, b"_anim_start_color")
        start_anim.setDuration(2000)
        start_anim.setStartValue(self._current_start_color if hasattr(self, '_current_start_color') else QColor("#87ceeb"))
        start_anim.setEndValue(QColor(start_color))
        start_anim.setEasingCurve(QEasingCurve.InOutQuad)
        
        end_anim = QPropertyAnimation(self, b"_anim_end_color")
        end_anim.setDuration(2000)
        end_anim.setStartValue(self._current_end_color if hasattr(self, '_current_end_color') else QColor("#f0e68c"))
        end_anim.setEndValue(QColor(end_color))
        end_anim.setEasingCurve(QEasingCurve.InOutQuad)
        
        # Stocker les couleurs actuelles
        self._current_start_color = QColor(start_color)
        self._current_end_color = QColor(end_color)
        
        # Ajouter les animations au groupe
        self._weather_animation_group.addAnimation(start_anim)
        self._weather_animation_group.addAnimation(end_anim)
        
        # Démarrer l'animation
        self._weather_animation_group.start()
    
    def _get_anim_start_color(self):
        return self._current_start_color if hasattr(self, '_current_start_color') else QColor("#87ceeb")
    
    def _set_anim_start_color(self, color):
        self._current_start_color = color
        self.update()
    
    def _get_anim_end_color(self):
        return self._current_end_color if hasattr(self, '_current_end_color') else QColor("#f0e68c")
    
    def _set_anim_end_color(self, color):
        self._current_end_color = color
        self.update()
    
    # Propriétés pour les animations de couleur
    _anim_start_color = Property(QColor, _get_anim_start_color, _set_anim_start_color)
    _anim_end_color = Property(QColor, _get_anim_end_color, _set_anim_end_color)

    def update_time(self):
        now = datetime.datetime.now()
        h = now.hour
        self.label_heure.setText(now.strftime("%H:%M"))
        self.label_secondes.setText(now.strftime(":%S"))

        jours = {
            "Monday": "Lundi", "Tuesday": "Mardi", "Wednesday": "Mercredi",
            "Thursday": "Jeudi", "Friday": "Vendredi", "Saturday": "Samedi", "Sunday": "Dimanche"
        }
        mois = {
            "January": "Janvier", "February": "Février", "March": "Mars", "April": "Avril",
            "May": "Mai", "June": "Juin", "July": "Juillet", "August": "Août",
            "September": "Septembre", "October": "Octobre", "November": "Novembre", "December": "Décembre"
        }
        jour_semaine = jours[now.strftime("%A")]
        mois_annee = mois[now.strftime("%B")]
        self.label_date.setText(f"{jour_semaine} {now.day} {mois_annee} {now.year}")

        # Saint du jour + période de la journée
        mois_jour = now.strftime("%m-%d")
        saint = SAINTS_DU_JOUR.get(mois_jour, "Saint inconnu")
        if 6 <= h < 12:
            periode = "Matin"
        elif h == 12:
            periode = "Midi"
        elif 12 < h < 18:
            periode = "Après-midi"
        elif 18 <= h < 22:
            periode = "Soir"
        else:
            periode = "Nuit"
        self.label_fete.setText(f"{saint} • {periode}")

        # Détection période (valeur de h déjà définie plus haut)
        #if h == 6 or h == 12 or h == 18 or h == 21:
            #self.show_overlay_message("Changement de période")
            #self.period_sound.play()

        if now.hour == 0:  # Chaque heure
            self.tick_sound.play()
        # Récupérer les données météo (désormais via un timer dédié)

        # Couleur dégradé selon l’heure
        if 6 <= h < 12:
            start, end = COLOR_THEMES["morning"]["start"], COLOR_THEMES["morning"]["end"]
        elif 12 <= h < 18:
            start, end = COLOR_THEMES["afternoon"]["start"], COLOR_THEMES["afternoon"]["end"]
        elif 18 <= h < 21:
            start, end = COLOR_THEMES["evening"]["start"], COLOR_THEMES["evening"]["end"]
        else:
            start, end = COLOR_THEMES["night"]["start"], COLOR_THEMES["night"]["end"]

        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0, QColor(start))
        grad.setColorAt(1, QColor(end))
        palette = self.palette()
        palette.setBrush(QPalette.Window, QBrush(grad))
        self.setPalette(palette)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # --- Détermination du thème en fonction de l'heure ---
        now = datetime.datetime.now()
        h = now.hour
        if 6 <= h < 12:
            theme = "morning"
        elif 12 <= h < 18:
            theme = "afternoon"
        elif 18 <= h < 21:
            theme = "evening"
        else:
            theme = "night"

        start, end = COLOR_THEMES[theme]["start"], COLOR_THEMES[theme]["end"]

        # --- Cadre interne ---
        rect_inner = self.rect().adjusted(10, 20, -10, -10)
        grad_inner = QLinearGradient(0, 0, 0, self.height())
        grad_inner.setColorAt(0, QColor(start))
        grad_inner.setColorAt(1, QColor(end))

        painter.setBrush(grad_inner)
        painter.setPen(QPen(QColor(30, 30, 30), 2))
        painter.drawRoundedRect(rect_inner, 10, 10)

        # --- Cadre externe ---
        pen_width = 20
        rect_ext = self.rect().adjusted(
            pen_width // 2,
            pen_width // 2,
            -(pen_width // 2) - 1,
            -(pen_width // 2) - 1
        )

        grad_border = QLinearGradient(0, 0, 0, self.height())
        grad_border.setColorAt(0, QColor(FRAME_GRADIENT["start"]))
        grad_border.setColorAt(1, QColor(FRAME_GRADIENT["end"]))

        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QBrush(grad_border), pen_width))
        painter.drawRoundedRect(rect_ext, 8, 8)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    horloge = Horloge()
    horloge.show()
    sys.exit(app.exec())
