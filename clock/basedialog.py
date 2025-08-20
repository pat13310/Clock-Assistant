import datetime
import json
import os
from PySide6.QtWidgets import QDialog, QPushButton, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QBrush, QLinearGradient

# Charger la configuration pour les thèmes/couleurs
def _load_config():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

_CONFIG = _load_config()
COLOR_THEMES = _CONFIG["color_themes"]
FRAME_GRADIENT = _CONFIG["frame_gradient"]

class BaseDialog(QDialog):
    """Classe de base pour toutes les boîtes de dialogue avec style uniforme"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        
        # Style semblable à l'horloge
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Marges par défaut pour tous les dialogs
        self._default_margins = (30, 40, 30, 20)  # gauche, haut, droite, bas
        
        # Style CSS commun
        self.setStyleSheet("""
            QDialog, QWidget#DialogBackground { background: transparent; }
            QLabel { color: white; font-weight: bold; }
            QLineEdit, QSpinBox, QTimeEdit, QComboBox, QTextEdit {
                background-color: rgba(0,0,0,120);
                color: white;
                border: 1px solid rgba(255,255,255,50);
                border-radius: 4px;
                padding: 2px 6px;
            }
            QCheckBox { color: white; font-weight: bold; }
            QPushButton {
                background-color: #555;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #666; }
            QPushButton:pressed { background-color: #444; }
            QDialogButtonBox QPushButton {
                background-color: #555;
                color: white;
                border-radius: 4px;
                padding: 4px 10px;
            }
            QDialogButtonBox QPushButton:hover { background-color: #666; }
            QListWidget {
                background-color: rgba(0,0,0,120);
                color: white;
                border: 1px solid rgba(255,255,255,50);
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid rgba(255,255,255,20);
            }
            QListWidget::item:selected {
                background-color: rgba(255,255,255,30);
            }
            QGroupBox {
                color: white;
                font-weight: bold;
                border: 1px solid rgba(255,255,255,50);
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        # Créer le bouton de fermeture rouge après l'initialisation
        self._create_close_button()
    
    def get_default_margins(self):
        """Retourne les marges par défaut pour les layouts"""
        return self._default_margins
    
    def _create_close_button(self):
        """Crée le bouton de fermeture rouge"""
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
        self.close_button.clicked.connect(self.reject)
        # Position initiale, sera ajustée dans resizeEvent
        # Positionner dans le coin en tenant compte des angles arrondis
        self.close_button.move(self.width() - 35, 2)
    
    def apply_text_shadow(self, label):
        """Applique un effet d'ombre portée à un QLabel"""
        if label is None:
            return
        effect = QGraphicsDropShadowEffect(self)
        effect.setBlurRadius(12)
        effect.setXOffset(2)
        effect.setYOffset(2)
        effect.setColor(QColor(0, 0, 0, 200))
        label.setGraphicsEffect(effect)
        if not hasattr(self, "_label_shadows"):
            self._label_shadows = []
        self._label_shadows.append(effect)
    
    def paintEvent(self, event):
        """Dessine le fond avec dégradé selon l'heure et angles arrondis"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Utiliser les mêmes paramètres que l'horloge principale
        pen_width_side = 25
        pen_width_bottom = 25
        
        # Fond intérieur avec dégradé et angles arrondis - plus de marge en haut
        rect_inner = self.rect().adjusted(pen_width_side+10, pen_width_side + 10, -pen_width_side-10, -pen_width_bottom)
        grad_inner = QLinearGradient(0, 0, 0, self.height())
        grad_inner.setColorAt(0, QColor(FRAME_GRADIENT["start"]))
        grad_inner.setColorAt(1, QColor(FRAME_GRADIENT["end"]))
        painter.setBrush(grad_inner)
        painter.setPen(QPen(QColor(30, 30, 30), 2))
        painter.drawRoundedRect(rect_inner, 10, 10)

        # Bordure extérieure avec angles arrondis
        rect_ext = self.rect().adjusted(
            pen_width_side // 2,
            pen_width_side // 2,
            -(pen_width_side // 2) - 1,
            -(pen_width_bottom // 2) - 1
        )
        grad_border = QLinearGradient(0, 0, 0, self.height())
        grad_border.setColorAt(0, QColor(FRAME_GRADIENT["start"]))
        grad_border.setColorAt(1, QColor(FRAME_GRADIENT["end"]))
        
        # Créer un anneau avec angles arrondis (comme dans l'horloge)
        from PySide6.QtGui import QPainterPath
        outer_rect = rect_ext
        inner_rect = rect_ext.adjusted(
            pen_width_side,
            pen_width_side,
            -pen_width_side,
            -pen_width_bottom
        )
        
        path_outer = QPainterPath()
        path_outer.addRoundedRect(outer_rect, 18, 18)
        path_inner = QPainterPath()
        path_inner.addRoundedRect(inner_rect, 10, 10)
        
        ring_path = path_outer.subtracted(path_inner)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(grad_border))
        painter.drawPath(ring_path)
    
    def resizeEvent(self, event):
        """Repositionne le bouton de fermeture lors du redimensionnement"""
        super().resizeEvent(event)
        if hasattr(self, 'close_button'):
            # Positionner dans le coin en tenant compte des angles arrondis
            self.close_button.move(self.width() - 30, 4)
