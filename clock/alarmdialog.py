import datetime
import json
import os
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QSpinBox, 
    QDialogButtonBox, QCheckBox, QListWidget, QListWidgetItem, QPushButton,
    QTimeEdit, QLabel, QComboBox, QTextEdit, QGroupBox
)
from PySide6.QtCore import QTimer, Qt, QTime, QObject, Signal
from PySide6.QtGui import QIcon
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QUrl
from basedialog import BaseDialog

class AlarmManager(QObject):
    """Gestionnaire des alarmes avec vérification périodique"""
    alarm_triggered = Signal(dict)  # Signal émis quand une alarme se déclenche
    
    def __init__(self):
        super().__init__()
        self.alarms = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_alarms)
        self.timer.start(1000)  # Vérifier toutes les secondes
        self.load_alarms()
        
        # Lecteur audio pour les alarmes
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        
    def load_alarms(self):
        """Charge les alarmes depuis le fichier JSON"""
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            alarms_path = os.path.join(base_dir, "alarms.json")
            if os.path.exists(alarms_path):
                with open(alarms_path, "r", encoding="utf-8") as f:
                    self.alarms = json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement des alarmes: {e}")
            self.alarms = []
    
    def save_alarms(self):
        """Sauvegarde les alarmes dans le fichier JSON"""
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            alarms_path = os.path.join(base_dir, "alarms.json")
            with open(alarms_path, "w", encoding="utf-8") as f:
                json.dump(self.alarms, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des alarmes: {e}")
    
    def add_alarm(self, alarm_data):
        """Ajoute une nouvelle alarme"""
        self.alarms.append(alarm_data)
        self.save_alarms()
    
    def remove_alarm(self, index):
        """Supprime une alarme par son index"""
        if 0 <= index < len(self.alarms):
            del self.alarms[index]
            self.save_alarms()
    
    def update_alarm(self, index, alarm_data):
        """Met à jour une alarme existante"""
        if 0 <= index < len(self.alarms):
            self.alarms[index] = alarm_data
            self.save_alarms()
    
    def check_alarms(self):
        """Vérifie si une alarme doit se déclencher"""
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M")
        current_day = now.weekday()  # 0 = lundi, 6 = dimanche
        
        for alarm in self.alarms:
            if not alarm.get("enabled", True):
                continue
                
            alarm_time = alarm.get("time", "")
            if alarm_time == current_time:
                # Vérifier les jours de répétition
                repeat_days = alarm.get("repeat_days", [])
                if not repeat_days or current_day in repeat_days:
                    self.trigger_alarm(alarm)
    
    def trigger_alarm(self, alarm):
        """Déclenche une alarme"""
        print(f"Alarme déclenchée: {alarm.get('name', 'Sans nom')}")
        
        # Jouer le son d'alarme
        sound_file = alarm.get("sound", "clock/audio/bell-ring-390294.mp3")
        if os.path.exists(sound_file):
            self.media_player.setSource(QUrl.fromLocalFile(os.path.abspath(sound_file)))
            self.media_player.play()
        
        # Émettre le signal pour notifier l'interface
        self.alarm_triggered.emit(alarm)
    
    def stop_current_alarm(self):
        """Arrête l'alarme sonore en cours"""
        if self.media_player.playbackState() == QMediaPlayer.PlayingState:
            self.media_player.stop()
            print("Alarme sonore arrêtée")

class AlarmDialog(BaseDialog):
    """Boîte de dialogue pour gérer les alarmes"""
    
    def __init__(self, alarm_manager, parent=None):
        super().__init__(parent)
        self.alarm_manager = alarm_manager
        self.setWindowTitle("Gestionnaire d'Alarmes")
        self.setWindowIcon(QIcon("clock/assets/alarm.svg"))
        self.setMinimumSize(500, 400)
        
        self.setup_ui()
        self.refresh_alarm_list()
        
        # Timer pour mettre à jour l'heure en temps réel
        self.time_update_timer = QTimer()
        self.time_update_timer.timeout.connect(self.update_current_time)
        self.time_update_timer.start(1000)  # Mise à jour chaque seconde
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(*self.get_default_margins())
        layout.setSpacing(10)
        
        # Liste des alarmes existantes
        alarms_group = QGroupBox("Alarmes configurées")
        alarms_layout = QVBoxLayout(alarms_group)
        
        self.alarm_list = QListWidget()
        self.alarm_list.itemClicked.connect(self.on_alarm_selected)
        alarms_layout.addWidget(self.alarm_list)
        
        # Boutons pour gérer les alarmes
        buttons_layout = QHBoxLayout()
        self.edit_button = QPushButton("Modifier")
        self.edit_button.clicked.connect(self.edit_alarm)
        self.edit_button.setEnabled(False)
        
        self.delete_button = QPushButton("Supprimer")
        self.delete_button.clicked.connect(self.delete_alarm)
        self.delete_button.setEnabled(False)
        
        buttons_layout.addWidget(self.edit_button)
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addStretch()
        
        alarms_layout.addLayout(buttons_layout)
        layout.addWidget(alarms_group)
        
        # Formulaire pour nouvelle alarme
        new_alarm_group = QGroupBox("Nouvelle alarme")
        form_layout = QFormLayout(new_alarm_group)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Nom de l'alarme")
        form_layout.addRow("Nom:", self.name_edit)
        
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")
        self.time_edit.setTime(QTime.currentTime())
        form_layout.addRow("Heure:", self.time_edit)
        
        # Jours de répétition
        days_layout = QHBoxLayout()
        self.day_checkboxes = []
        days = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
        for i, day in enumerate(days):
            checkbox = QCheckBox(day)
            checkbox.setProperty("day_index", i)
            self.day_checkboxes.append(checkbox)
            days_layout.addWidget(checkbox)
        
        # Bouton "Tous" pour sélectionner/désélectionner tous les jours
        self.all_days_button = QPushButton("Tous")
        self.all_days_button.setMaximumWidth(60)
        self.all_days_button.clicked.connect(self.toggle_all_days)
        days_layout.addWidget(self.all_days_button)
        
        form_layout.addRow("Répéter:", days_layout)
        
        # Son d'alarme
        self.sound_combo = QComboBox()
        self.populate_sound_combo()
        form_layout.addRow("Son:", self.sound_combo)
        
        # Message personnalisé
        self.message_edit = QTextEdit()
        self.message_edit.setMaximumHeight(60)
        self.message_edit.setPlaceholderText("Message personnalisé (optionnel)")
        form_layout.addRow("Message:", self.message_edit)
        
        # Alarme activée
        self.enabled_checkbox = QCheckBox("Alarme activée")
        self.enabled_checkbox.setChecked(True)
        form_layout.addRow("", self.enabled_checkbox)
        
        layout.addWidget(new_alarm_group)
        
        # Boutons de dialogue
        dialog_buttons = QDialogButtonBox()
        
        add_button = QPushButton("Ajouter Alarme")
        add_button.clicked.connect(self.add_alarm)
        
        close_button = QPushButton("Fermer")
        close_button.clicked.connect(self.accept)
        
        dialog_buttons.addButton(add_button, QDialogButtonBox.ActionRole)
        dialog_buttons.addButton(close_button, QDialogButtonBox.RejectRole)
        
        layout.addWidget(dialog_buttons)
        
        # Appliquer l'ombrage aux libellés
        self.apply_label_shadows(form_layout)
    
    def populate_sound_combo(self):
        """Remplit la liste des sons disponibles"""
        audio_dir = "clock/audio"
        if os.path.exists(audio_dir):
            sound_files = [f for f in os.listdir(audio_dir) if f.endswith(('.mp3', '.wav'))]
            for sound_file in sound_files:
                display_name = os.path.splitext(sound_file)[0].replace('-', ' ').title()
                self.sound_combo.addItem(display_name, os.path.join(audio_dir, sound_file))
        
        # Son par défaut
        if self.sound_combo.count() == 0:
            self.sound_combo.addItem("Son par défaut", "clock/audio/bell-ring-390294.mp3")
    
    def refresh_alarm_list(self):
        """Actualise la liste des alarmes"""
        self.alarm_list.clear()
        for i, alarm in enumerate(self.alarm_manager.alarms):
            name = alarm.get("name", f"Alarme {i+1}")
            time = alarm.get("time", "00:00")
            enabled = "✓" if alarm.get("enabled", True) else "✗"
            
            # Jours de répétition
            repeat_days = alarm.get("repeat_days", [])
            if repeat_days:
                days_text = ", ".join([["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"][d] for d in repeat_days])
            else:
                days_text = "Une fois"
            
            item_text = f"{enabled} {name} - {time} ({days_text})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, i)  # Stocker l'index
            self.alarm_list.addItem(item)
    
    def on_alarm_selected(self, item):
        """Appelé quand une alarme est sélectionnée"""
        self.edit_button.setEnabled(True)
        self.delete_button.setEnabled(True)
    
    def add_alarm(self):
        """Ajoute une nouvelle alarme"""
        if not self.name_edit.text().strip():
            return
        
        # Récupérer les jours sélectionnés
        repeat_days = []
        for checkbox in self.day_checkboxes:
            if checkbox.isChecked():
                repeat_days.append(checkbox.property("day_index"))
        
        alarm_data = {
            "name": self.name_edit.text().strip(),
            "time": self.time_edit.time().toString("HH:mm"),
            "repeat_days": repeat_days,
            "sound": self.sound_combo.currentData() or "clock/audio/bell-ring-390294.mp3",
            "message": self.message_edit.toPlainText().strip(),
            "enabled": self.enabled_checkbox.isChecked()
        }
        
        self.alarm_manager.add_alarm(alarm_data)
        self.refresh_alarm_list()
        self.clear_form()
    
    def edit_alarm(self):
        """Modifie l'alarme sélectionnée"""
        current_item = self.alarm_list.currentItem()
        if not current_item:
            return
        
        index = current_item.data(Qt.UserRole)
        alarm = self.alarm_manager.alarms[index]
        
        # Remplir le formulaire avec les données existantes
        self.name_edit.setText(alarm.get("name", ""))
        time_parts = alarm.get("time", "00:00").split(":")
        self.time_edit.setTime(QTime(int(time_parts[0]), int(time_parts[1])))
        
        # Cocher les jours appropriés
        repeat_days = alarm.get("repeat_days", [])
        for checkbox in self.day_checkboxes:
            day_index = checkbox.property("day_index")
            checkbox.setChecked(day_index in repeat_days)
        
        # Sélectionner le bon son
        sound_path = alarm.get("sound", "")
        for i in range(self.sound_combo.count()):
            if self.sound_combo.itemData(i) == sound_path:
                self.sound_combo.setCurrentIndex(i)
                break
        
        self.message_edit.setPlainText(alarm.get("message", ""))
        self.enabled_checkbox.setChecked(alarm.get("enabled", True))
        
        # Changer le bouton "Ajouter" en "Mettre à jour"
        # (Pour simplifier, on supprime l'ancienne et on ajoute la nouvelle)
        self.alarm_manager.remove_alarm(index)
        self.refresh_alarm_list()
    
    def delete_alarm(self):
        """Supprime l'alarme sélectionnée"""
        current_item = self.alarm_list.currentItem()
        if not current_item:
            return
        
        index = current_item.data(Qt.UserRole)
        self.alarm_manager.remove_alarm(index)
        self.refresh_alarm_list()
        self.edit_button.setEnabled(False)
        self.delete_button.setEnabled(False)
    
    def update_current_time(self):
        """Met à jour l'heure actuelle dans le QTimeEdit si aucune alarme n'est en cours d'édition"""
        # Ne mettre à jour que si le formulaire est vide (nouvelle alarme)
        if (self.name_edit.text().strip() == "" and 
            not any(checkbox.isChecked() for checkbox in self.day_checkboxes)):
            self.time_edit.setTime(QTime.currentTime())
    
    def toggle_all_days(self):
        """Sélectionne ou désélectionne tous les jours de la semaine"""
        # Vérifier si tous les jours sont déjà sélectionnés
        all_checked = all(checkbox.isChecked() for checkbox in self.day_checkboxes)
        
        # Si tous sont cochés, les décocher, sinon les cocher tous
        new_state = not all_checked
        for checkbox in self.day_checkboxes:
            checkbox.setChecked(new_state)
    
    def clear_form(self):
        """Vide le formulaire"""
        self.name_edit.clear()
        self.time_edit.setTime(QTime.currentTime())
        for checkbox in self.day_checkboxes:
            checkbox.setChecked(False)
        self.sound_combo.setCurrentIndex(0)
        self.message_edit.clear()
        self.enabled_checkbox.setChecked(True)
    
    def apply_label_shadows(self, form):
        """Applique l'ombrage à tous les libellés du formulaire"""
        for i in range(form.rowCount()):
            label = form.itemAt(i, QFormLayout.LabelRole)
            if label and label.widget():
                self.apply_text_shadow(label.widget())
