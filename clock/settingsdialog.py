import datetime

from PySide6.QtWidgets import (
    QFormLayout, QLineEdit, QSpinBox, QDialogButtonBox, QCheckBox
)
from PySide6.QtGui import QIcon
from basedialog import BaseDialog


class SettingsDialog(BaseDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Paramètres")
        self.setWindowIcon(QIcon("clock/assets/settings.svg"))
        self._config = config
        self.setMinimumSize(420, 300)

        form = QFormLayout(self)
        form.setContentsMargins(*self.get_default_margins())
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

        # Appliquer l'ombrage aux libellés
        self.apply_label_shadows(form)

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

    def apply_label_shadows(self, form):
        """Applique l'ombrage à tous les libellés du formulaire."""
        champs = [
            self.title_edit,
            self.width_spin,
            self.height_spin,
            self.signature_edit,
            self.shadows_check,
            self.show_signature_check,
            self.weather_refresh_spin,
            self.show_weather_bar_check,
        ]
        for champ in champs:
            lbl = form.labelForField(champ)
            self.apply_text_shadow(lbl)
