
from PySide6.QtWidgets import    QLabel
from PySide6.QtGui import    QColor, QPainter, QPen

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

