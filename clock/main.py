import sys
import random
import datetime
import math
import pyttsx3
import requests

from PySide6.QtGui import QColor, QBrush, QFont, QLinearGradient, QRadialGradient, QPainterPath, QPen
from PySide6.QtWidgets import (
    QApplication, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem,
    QGraphicsRectItem, QGraphicsTextItem, QMainWindow, QGraphicsItem, QGraphicsDropShadowEffect, QGraphicsPathItem
)
from PySide6.QtCore import Qt, QTimer, QPointF, QPropertyAnimation, QObject, Property, QEasingCurve
from PySide6.QtGui import QColor, QBrush, QFont, QLinearGradient
from PySide6.QtWidgets import (
    QApplication, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem,
    QGraphicsRectItem, QGraphicsTextItem, QMainWindow
)


# ============================
#   Classes animables
# ============================

from PySide6.QtCore import QRectF

class AnimEllipse(QGraphicsEllipseItem, QObject):
    def __init__(self, rect, color, parent=None):
        # rect est un tuple (x, y, w, h)
        x, y, w, h = rect
        QGraphicsEllipseItem.__init__(self, x, y, w, h, parent)
        QObject.__init__(self)
        self.setBrush(QBrush(QColor(color)))

    def get_pos(self): return self.pos()
    def set_pos(self, p): self.setPos(p)
    
    def get_rotation(self): return super().rotation()
    def set_rotation(self, r): self.setRotation(r)
    
    def get_opacity(self): return super().opacity()
    def set_opacity(self, o): self.setOpacity(o)

    pos_anim = Property(QPointF, fget=get_pos, fset=set_pos)
    rotation = Property(float, fget=get_rotation, fset=set_rotation)
    opacity = Property(float, fget=get_opacity, fset=set_opacity)


class AnimRect(QGraphicsRectItem, QObject):
    def __init__(self, rect, color, parent=None):
        # rect est un tuple (x, y, w, h)
        x, y, w, h = rect
        QGraphicsRectItem.__init__(self, x, y, w, h, parent)
        QObject.__init__(self)
        self.setBrush(QBrush(QColor(color)))

    def get_pos(self): return self.pos()
    def set_pos(self, p): self.setPos(p)
    
    def get_rotation(self): return super().rotation()
    def set_rotation(self, r): self.setRotation(r)

    pos_anim = Property(QPointF, fget=get_pos, fset=set_pos)
    rotation = Property(float, fget=get_rotation, fset=set_rotation)

class SunItem(QGraphicsItem, QObject):
    def __init__(self, x, y, parent=None):
        QGraphicsItem.__init__(self, parent)
        QObject.__init__(self)
        self.setPos(x, y)
        self.sun_radius = 40
        self.ray_length = 20
        self.ray_width = 3
        self.animation_scale = 1.0
        self.ray_animation_value = 0.0
        
    def boundingRect(self):
        # Définir la zone de dessin (avec marge pour les rayons)
        margin = self.ray_length + 10
        diameter = (self.sun_radius + self.ray_length) * 2
        return QRectF(-diameter/2 - margin, -diameter/2 - margin, 
                       diameter + 2*margin, diameter + 2*margin)
    
    def paint(self, painter, option, widget):
        # Dessiner le soleil avec dégradé
        gradient = QRadialGradient(0, 0, self.sun_radius)
        gradient.setColorAt(0, QColor(255, 255, 200))  # Jaune clair au centre
        gradient.setColorAt(0.7, QColor(255, 200, 0))  # Orange
        gradient.setColorAt(1, QColor(255, 165, 0))    # Orange foncé à l'extérieur
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        
        # Appliquer l'échelle d'animation
        painter.save()
        painter.scale(self.animation_scale, self.animation_scale)
        
        # Dessiner le disque du soleil
        painter.drawEllipse(-self.sun_radius, -self.sun_radius, 
                           self.sun_radius*2, self.sun_radius*2)
        
        # Dessiner les rayons
        # Utiliser la valeur d'animation pour faire varier la taille des rayons
        animated_ray_length = self.ray_length + self.ray_animation_value * 5
        animated_ray_width = self.ray_width + self.ray_animation_value * 1
        
        painter.setBrush(QBrush(QColor(255, 200, 0, 180)))  # Orange semi-transparent
        painter.setPen(Qt.NoPen)
        
        # Nombre de rayons
        ray_count = 12
        angle_step = 360.0 / ray_count
        
        for i in range(ray_count):
            angle = i * angle_step
            # Convertir l'angle en radians
            rad = angle * 3.14159 / 180
            
            # Position de départ du rayon (sur le bord du soleil)
            start_x = (self.sun_radius) * math.cos(rad)
            start_y = (self.sun_radius) * math.sin(rad)
            
            # Position de fin du rayon
            end_x = (self.sun_radius + animated_ray_length) * math.cos(rad)
            end_y = (self.sun_radius + animated_ray_length) * math.sin(rad)
            
            # Dessiner le rayon comme un triangle
            painter.save()
            painter.translate(start_x, start_y)
            painter.rotate(angle)
            # Créer un chemin pour le triangle
            path = QPainterPath()
            path.moveTo(0, 0)
            path.lineTo(animated_ray_width, animated_ray_length)
            path.lineTo(-animated_ray_width, animated_ray_length)
            path.closeSubpath()
            painter.fillPath(path, QBrush(QColor(255, 200, 0, 180)))
            painter.restore()
        
        painter.restore()
    
    def set_animation_scale(self, scale):
        self.animation_scale = scale
        self.update()
        
    def set_ray_animation_value(self, value):
        self.ray_animation_value = value
        self.update()
        
    def get_pos(self): return self.pos()
    def set_pos(self, p): self.setPos(p)
    
    def get_rotation(self): return super().rotation()
    def set_rotation(self, r): self.setRotation(r)

    pos_anim = Property(QPointF, fget=get_pos, fset=set_pos)
    rotation = Property(float, fget=get_rotation, fset=set_rotation)
    ray_animation = Property(float, fget=lambda self: self.ray_animation_value, fset=set_ray_animation_value)

# ============================
#   Gestion météo
# ============================

class MeteoManager:
    def __init__(self, scene):
        self.scene = scene
        self.items_actifs = []

    def clear_weather(self):
        for item in self.items_actifs:
            # Vérifier si l'élément est un QGraphicsItem ou une animation
            if hasattr(item, 'scene') and callable(getattr(item, 'scene')):
                # C'est un QGraphicsItem, on le retire de la scène
                self.scene.removeItem(item)
            elif hasattr(item, 'stop') and callable(getattr(item, 'stop')):
                # C'est une animation, on l'arrête
                item.stop()
        self.items_actifs.clear()

    def soleil(self):
        self.clear_weather()
        soleil = SunItem(0, 0)  # Position initiale à (0, 0), sera animée
        self.scene.addItem(soleil)
        self.items_actifs.append(soleil)
        
        # Stocker le soleil pour mise à jour de position
        self.sun_item = soleil

        # Animation de rotation
        anim_rotation = QPropertyAnimation(soleil, b"rotation")
        anim_rotation.setDuration(16000)  # Ralentir l'animation (16 secondes pour un tour complet)
        anim_rotation.setStartValue(0)
        anim_rotation.setEndValue(360)
        anim_rotation.setLoopCount(-1)
        anim_rotation.setEasingCurve(QEasingCurve.InOutCubic)  # Courbe d'animation plus naturelle
        anim_rotation.start()
        self.items_actifs.append(anim_rotation)
        
        # Animation de pulsation
        anim_pulse = QPropertyAnimation(soleil, b"animation_scale")
        anim_pulse.setDuration(4000)
        anim_pulse.setStartValue(1.0)
        anim_pulse.setKeyValueAt(0.5, 1.1)  # Expansion à 110%
        anim_pulse.setEndValue(1.0)       # Retour à 100%
        anim_pulse.setLoopCount(-1)
        anim_pulse.setEasingCurve(QEasingCurve.InOutSine)
        anim_pulse.start()
        self.items_actifs.append(anim_pulse)
        
        # Animation des rayons
        anim_rays = QPropertyAnimation(soleil, b"ray_animation")
        anim_rays.setDuration(2000)
        anim_rays.setStartValue(0.0)
        anim_rays.setKeyValueAt(0.5, 1.0)
        anim_rays.setEndValue(0.0)
        anim_rays.setLoopCount(-1)
        anim_rays.setEasingCurve(QEasingCurve.InOutSine)
        anim_rays.start()
        self.items_actifs.append(anim_rays)
        
        # Mettre à jour la position initiale du soleil
        self.update_sun_position(False)
        
    def update_sun_position(self, has_clouds=False):
        """Met à jour la position du soleil selon l'heure actuelle"""
        # Obtenir l'heure actuelle
        now = datetime.datetime.now()
        hour = now.hour + now.minute / 60.0  # Convertir en heures décimales
        
        # Définir les limites de la trajectoire du soleil
        x_min, x_max = -100, 900  # Limites horizontales
        y_min, y_max = 80, 300    # Limites verticales (zénith à l'horizon)
        
        # Si il y a des nuages, faire descendre un peu le soleil
        if has_clouds:
            y_min += 20
            y_max += 20
        
        # Calculer la position selon une courbe parabolique
        # Le soleil se lève à 6h et se couche à 22h (16 heures de jour)
        sunrise = 6.0
        sunset = 22.0
        day_length = sunset - sunrise
        
        if sunrise <= hour <= sunset:
            # Le soleil est visible
            # Normaliser l'heure entre 0 et 1 (0 = lever, 1 = coucher)
            normalized_time = (hour - sunrise) / day_length
            
            # Calculer la position X (linéaire)
            x = x_min + (x_max - x_min) * normalized_time
            
            # Calculer la position Y (parabolique)
            # La parabole a son sommet au milieu de la journée
            y = y_min + (y_max - y_min) * (1 - (2 * normalized_time - 1) ** 2)
            
            # Mettre à jour la position du soleil
            if hasattr(self, 'sun_item'):
                self.sun_item.setPos(x, y)
        else:
            # Le soleil n'est pas visible (nuit)
            # Le retirer de la scène
            if hasattr(self, 'sun_item') and self.sun_item.scene() is not None:
                self.scene.removeItem(self.sun_item)

    def nuages(self):
        self.clear_weather()
        for i in range(3):
            nuage = AnimEllipse((0, 0, 100, 60), "lightgray")
            y = 50 + i * 60
            nuage.setPos(-150, y)
            self.scene.addItem(nuage)
            self.items_actifs.append(nuage)

            anim = QPropertyAnimation(nuage, b"pos_anim")
            anim.setDuration(20000)
            anim.setStartValue(QPointF(-150, y))
            anim.setEndValue(QPointF(900, y))
            anim.setLoopCount(-1)
            anim.start()
            self.items_actifs.append(anim)
            
    def soleil_et_un_nuage(self):
        """Affiche le soleil avec un nuage léger"""
        self.clear_weather()
        
        # Ajouter un nuage léger
        nuage = AnimEllipse((0, 0, 80, 40), "white")  # Nuage blanc et plus petit
        nuage.setPos(-100, 100)  # Positionner le nuage en haut de l'écran
        self.scene.addItem(nuage)
        self.items_actifs.append(nuage)

        # Animation du nuage
        anim = QPropertyAnimation(nuage, b"pos_anim")
        anim.setDuration(30000)  # Un peu plus lent que le soleil
        anim.setStartValue(QPointF(-100, 100))
        anim.setEndValue(QPointF(900, 100))
        anim.setLoopCount(-1)
        anim.start()
        self.items_actifs.append(anim)
        
        # Ajouter le soleil (au premier plan)
        soleil = SunItem(0, 0)  # Position initiale à (0, 0), sera animée
        self.scene.addItem(soleil)
        self.items_actifs.append(soleil)
        
        # Stocker le soleil pour mise à jour de position
        self.sun_item = soleil

        # Animation de rotation
        anim_rotation = QPropertyAnimation(soleil, b"rotation")
        anim_rotation.setDuration(16000)  # Ralentir l'animation (16 secondes pour un tour complet)
        anim_rotation.setStartValue(0)
        anim_rotation.setEndValue(360)
        anim_rotation.setLoopCount(-1)
        anim_rotation.setEasingCurve(QEasingCurve.InOutCubic)  # Courbe d'animation plus naturelle
        anim_rotation.start()
        self.items_actifs.append(anim_rotation)
        
        # Animation de pulsation
        anim_pulse = QPropertyAnimation(soleil, b"animation_scale")
        anim_pulse.setDuration(4000)
        anim_pulse.setStartValue(1.0)
        anim_pulse.setKeyValueAt(0.5, 1.1)  # Expansion à 110%
        anim_pulse.setEndValue(1.0)       # Retour à 100%
        anim_pulse.setLoopCount(-1)
        anim_pulse.setEasingCurve(QEasingCurve.InOutSine)
        anim_pulse.start()
        self.items_actifs.append(anim_pulse)
        
        # Animation des rayons
        anim_rays = QPropertyAnimation(soleil, b"ray_animation")
        anim_rays.setDuration(2000)
        anim_rays.setStartValue(0.0)
        anim_rays.setKeyValueAt(0.5, 1.0)
        anim_rays.setEndValue(0.0)
        anim_rays.setLoopCount(-1)
        anim_rays.setEasingCurve(QEasingCurve.InOutSine)
        anim_rays.start()
        self.items_actifs.append(anim_rays)
        
        # Mettre à jour la position initiale du soleil
        self.update_sun_position(False)
        
    def soleil_et_nuages(self):
        """Affiche le soleil avec des nuages en arrière-plan"""
        self.clear_weather()
        
        # Ajouter les nuages en arrière-plan (toujours en dessous du soleil)
        # Première couche de nuages (gris clair)
        for i in range(3):
            nuage = AnimEllipse((0, 0, 120, 70), "#D3D3D3")  # Gris clair
            y = 350 + i * 80  # Positionner les nuages dans la partie inférieure
            nuage.setPos(-150, y)
            self.scene.addItem(nuage)
            self.items_actifs.append(nuage)

            anim = QPropertyAnimation(nuage, b"pos_anim")
            anim.setDuration(25000)  # Un peu plus lent que le soleil
            anim.setStartValue(QPointF(-150, y))
            anim.setEndValue(QPointF(900, y))
            anim.setLoopCount(-1)
            anim.start()
            self.items_actifs.append(anim)
            
        # Deuxième couche de nuages (gris plus foncé)
        for i in range(2):
            nuage = AnimEllipse((0, 0, 100, 60), "#A9A9A9")  # Gris foncé
            y = 380 + i * 100  # Positionner légèrement plus bas
            nuage.setPos(-100, y)
            self.scene.addItem(nuage)
            self.items_actifs.append(nuage)

            anim = QPropertyAnimation(nuage, b"pos_anim")
            anim.setDuration(30000)  # Encore plus lent
            anim.setStartValue(QPointF(-100, y))
            anim.setEndValue(QPointF(900, y))
            anim.setLoopCount(-1)
            anim.start()
            self.items_actifs.append(anim)
        
        # Ajouter le soleil (au premier plan)
        soleil = SunItem(0, 0)  # Position initiale à (0, 0), sera animée
        self.scene.addItem(soleil)
        self.items_actifs.append(soleil)
        
        # Stocker le soleil pour mise à jour de position
        self.sun_item = soleil

        # Animation de rotation
        anim_rotation = QPropertyAnimation(soleil, b"rotation")
        anim_rotation.setDuration(16000)  # Ralentir l'animation (16 secondes pour un tour complet)
        anim_rotation.setStartValue(0)
        anim_rotation.setEndValue(360)
        anim_rotation.setLoopCount(-1)
        anim_rotation.setEasingCurve(QEasingCurve.InOutCubic)  # Courbe d'animation plus naturelle
        anim_rotation.start()
        self.items_actifs.append(anim_rotation)
        
        # Animation de pulsation
        anim_pulse = QPropertyAnimation(soleil, b"animation_scale")
        anim_pulse.setDuration(4000)
        anim_pulse.setStartValue(1.0)
        anim_pulse.setKeyValueAt(0.5, 1.1)  # Expansion à 110%
        anim_pulse.setEndValue(1.0)       # Retour à 100%
        anim_pulse.setLoopCount(-1)
        anim_pulse.setEasingCurve(QEasingCurve.InOutSine)
        anim_pulse.start()
        self.items_actifs.append(anim_pulse)
        
        # Animation des rayons
        anim_rays = QPropertyAnimation(soleil, b"ray_animation")
        anim_rays.setDuration(2000)
        anim_rays.setStartValue(0.0)
        anim_rays.setKeyValueAt(0.5, 1.0)
        anim_rays.setEndValue(0.0)
        anim_rays.setLoopCount(-1)
        anim_rays.setEasingCurve(QEasingCurve.InOutSine)
        anim_rays.start()
        self.items_actifs.append(anim_rays)
        
        # Mettre à jour la position initiale du soleil
        self.update_sun_position(True)

    def pluie(self):
        self.clear_weather()
        for _ in range(50):
            goutte = AnimRect((0, 0, 2, 10), "blue")
            x = random.randint(0, 800)
            y = random.randint(-400, 0)
            goutte.setPos(x, y)
            self.scene.addItem(goutte)
            self.items_actifs.append(goutte)

            anim = QPropertyAnimation(goutte, b"pos_anim")
            anim.setDuration(random.randint(2000, 4000))
            anim.setStartValue(QPointF(x, y))
            anim.setEndValue(QPointF(x, 450))
            anim.setLoopCount(-1)
            anim.start()
            self.items_actifs.append(anim)

    def neige(self):
        self.clear_weather()
        for _ in range(30):
            flocon = AnimEllipse((0, 0, 8, 8), "white")
            x = random.randint(0, 800)
            y = random.randint(-400, 0)
            flocon.setPos(x, y)
            self.scene.addItem(flocon)
            self.items_actifs.append(flocon)

            anim = QPropertyAnimation(flocon, b"pos_anim")
            anim.setDuration(random.randint(4000, 8000))
            anim.setStartValue(QPointF(x, y))
            anim.setEndValue(QPointF(x + random.randint(-50, 50), 450))
            anim.setLoopCount(-1)
            anim.start()
            self.items_actifs.append(anim)

    def orage(self):
        self.clear_weather()
        eclair = AnimRect((0, 0, 40, 120), "yellow")
        eclair.setPos(380, 50)
        self.scene.addItem(eclair)
        self.items_actifs.append(eclair)

        anim = QPropertyAnimation(eclair, b"opacity")
        anim.setDuration(400)
        anim.setStartValue(0)
        anim.setKeyValueAt(0.5, 1)
        anim.setEndValue(0)
        anim.setLoopCount(-1)
        anim.start()
        self.items_actifs.append(anim)


# ============================
#   Fonctions API météo
# ============================

def get_weather_data(city="Paris"):
    """
    Récupère les données météo pour une ville donnée.
    Utilise l'API OpenWeatherMap.
    """
    API_KEY = "0c412981a35ed28fc18aac9ef4715ab9"  # Remplacer par une clé API valide
    BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
    
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",  # Température en Celsius
        "lang": "fr"  # Description en français
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()  # Lève une exception pour les codes d'erreur HTTP
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération des données météo: {e}")
        return None

def get_weather_condition(weather_data):
    """
    Détermine la condition météo à partir des données de l'API.
    """
    if not weather_data:
        return "clear"  # Par défaut, ciel dégagé
    
    weather_id = weather_data["weather"][0]["id"]
    
    # Classification simplifiée des conditions météo
    if 200 <= weather_id < 300:  # Orage
        return "storm"
    elif 300 <= weather_id < 400:  # Bruine
        return "rain"
    elif 500 <= weather_id < 600:  # Pluie
        return "rain"
    elif 600 <= weather_id < 700:  # Neige
        return "snow"
    elif 700 <= weather_id < 800:  # Atmosphère (brume, brouillard, etc.)
        return "clouds"
    elif weather_id == 800:  # Ciel dégagé
        return "clear"
    elif 801 <= weather_id < 900:  # Nuages
        # Identifier les conditions partiellement nuageuses
        if weather_id == 802 or weather_id == 803 or weather_id == 804:
            return "partially_cloudy"  # Partiellement nuageux
        else:
            return "clouds"  # Nuageux
    else:
        return "clear"  # Par défaut

# ============================
#   Fenêtre principale
# ============================

class Horloge(QMainWindow):
    # Dégradés pour chaque type de météo
    WEATHER_GRADIENTS = {
        "Matin": (QColor(135, 206, 250), QColor(255, 255, 200)),  # Ciel bleu clair vers jaune pâle
        "Midi": (QColor(135, 206, 250), QColor(255, 255, 200)),  # Ciel bleu clair vers jaune pâle (même que Matin)
        "Après-midi": (QColor(135, 206, 235), QColor(200, 200, 200)),  # Ciel bleu vers gris clair
        "Soir": (QColor(70, 130, 180), QColor(192, 192, 192)),  # Ciel bleu foncé vers gris
        "Nuit": (QColor(25, 25, 112), QColor(0, 0, 0)),  # Bleu nuit vers noir
        "Orage": (QColor(105, 105, 105), QColor(0, 0, 0))  # Gris sombre vers noir
    }
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Assistant Horloge")
        self.resize(800, 480)

        # Scène graphique
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)
        
        # Initialize background
        self.update_background("Matin")

        # Texte affiché (heure)
        self.text_item = QGraphicsTextItem("")
        self.text_item.setDefaultTextColor(Qt.white)
        self.text_item.setFont(QFont("Arial", 48, QFont.Bold))  # Augmenter la taille de la police
        self.text_item.setPos(20, 20)
        # Ajouter un effet d'ombre
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(5)
        shadow_effect.setXOffset(2)
        shadow_effect.setYOffset(2)
        shadow_effect.setColor(QColor(0, 0, 0, 150))  # Noir semi-transparent
        self.text_item.setGraphicsEffect(shadow_effect)
        self.scene.addItem(self.text_item)

        # Cadre pour les informations météo détaillées
        # Créer un chemin pour le cadre avec des coins arrondis
        path = QPainterPath()
        path.addRoundedRect(10, 390, 780, 80, 10, 10)  # Position, taille et rayon des coins (en bas de l'écran)
        self.weather_info_frame = QGraphicsPathItem(path)
        self.weather_info_frame.setBrush(QBrush(QColor(0, 0, 0, 80)))  # Noir plus translucide
        self.weather_info_frame.setPen(QPen(QColor(255, 255, 255, 100), 1))  # Bordure blanche semi-transparente
        # Ajouter un effet d'ombre au cadre
        frame_shadow_effect = QGraphicsDropShadowEffect()
        frame_shadow_effect.setBlurRadius(10)
        frame_shadow_effect.setXOffset(3)
        frame_shadow_effect.setYOffset(3)
        frame_shadow_effect.setColor(QColor(0, 0, 0, 150))  # Noir semi-transparent
        self.weather_info_frame.setGraphicsEffect(frame_shadow_effect)
        self.scene.addItem(self.weather_info_frame)

        # Texte pour les informations météo détaillées
        self.weather_info_item = QGraphicsTextItem("")
        self.weather_info_item.setDefaultTextColor(Qt.white)
        self.weather_info_item.setFont(QFont("Arial", 14, QFont.Normal))
        self.weather_info_item.setPos(20, 400)  # Ajuster la position pour qu'il soit dans le cadre (en bas de l'écran)
        # Ajouter un effet d'ombre
        shadow_effect2 = QGraphicsDropShadowEffect()
        shadow_effect2.setBlurRadius(5)
        shadow_effect2.setXOffset(1)
        shadow_effect2.setYOffset(1)
        shadow_effect2.setColor(QColor(0, 0, 0, 150))  # Noir semi-transparent
        self.weather_info_item.setGraphicsEffect(shadow_effect2)
        self.scene.addItem(self.weather_info_item)

        # Gestion météo
        self.meteo = MeteoManager(self.scene)

        # Synthèse vocale
        self.engine = pyttsx3.init()

        # Timer pour mise à jour
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        # Timer pour mise à jour de la météo (toutes les 10 minutes)
        self.weather_timer = QTimer()
        self.weather_timer.timeout.connect(self.update_weather)
        self.weather_timer.start(600000)  # 600000 ms = 10 minutes

        self.update_time()
        self.update_weather()  # Mise à jour initiale de la météo

    def update_time(self):
        now = datetime.datetime.now()
        h = now.hour

        if 6 <= h < 12:
            periode = "Matin"
        elif h == 12 and now.minute < 30:
            periode = "Midi"
        elif 12 <= h < 18:
            periode = "Après-midi"
        elif 18 <= h < 22:
            periode = "Soir"
        else:
            periode = "Nuit"
        
        # Ne pas mettre à jour l'heure chaque seconde, mais seulement la période
        # Récupérer le texte actuel
        current_text = self.text_item.toPlainText()
        # Extraire l'heure si elle existe déjà
        if " - " in current_text:
            heure = current_text.split(" - ")[0]
        else:
            # Si l'heure n'existe pas encore, utiliser l'heure actuelle
            heure = now.strftime('%H:%M:%S')
        
        self.text_item.setPlainText(f"{heure} - {periode}")
        self.update_background(periode)
        
        # Mettre à jour la position du soleil
        if hasattr(self.meteo, 'update_sun_position'):
            # Déterminer si on affiche des nuages
            weather_data = get_weather_data()
            if weather_data:
                condition = get_weather_condition(weather_data)
                has_clouds = (condition == "partially_cloudy" or condition == "clouds")
            else:
                has_clouds = False
            self.meteo.update_sun_position(has_clouds)

    def update_weather(self):
        """
        Met à jour l'affichage météo en fonction des données de l'API.
        """
        # Récupérer les données météo pour afficher la température
        weather_data = get_weather_data()
        if weather_data:
            condition = get_weather_condition(weather_data)
            temperature = weather_data["main"]["temp"]
            pressure = weather_data["main"]["pressure"]
            wind_speed = weather_data["wind"]["speed"]
            humidity = weather_data["main"]["humidity"]
            visibility = weather_data["visibility"]
            description = weather_data["weather"][0]["description"]
            
            # Mettre à jour le texte avec la température
            current_text = self.text_item.toPlainText()
            self.text_item.setPlainText(f"{current_text} - {temperature}°C")
            
            # Mettre à jour le texte avec les informations météo détaillées
            weather_info = f"🌡️ {temperature}°C  📊 {pressure} hPa  💨 {wind_speed} m/s\n"
            weather_info += f"💧 {humidity}%  👀 {visibility}m  🌤️ {description}"
            self.weather_info_item.setPlainText(weather_info)
            
            # Mettre à jour l'animation météo selon la condition
            if condition == "partially_cloudy":
                self.meteo.soleil_et_nuages()
            elif condition == "clear":
                self.meteo.soleil_et_un_nuage()
            else:
                # Toujours afficher le soleil pour les autres conditions
                self.meteo.soleil()

    def update_background(self, period):
        """Met à jour le fond avec un dégradé selon la période"""
        if period in self.WEATHER_GRADIENTS:
            start_color, end_color = self.WEATHER_GRADIENTS[period]
            gradient = QLinearGradient(0, 0, 0, self.scene.height())
            gradient.setColorAt(0, start_color)
            gradient.setColorAt(1, end_color)
            self.scene.setBackgroundBrush(QBrush(gradient))
    
    def keyPressEvent(self, event):
        """Affiche un message temporaire quand l’utilisateur demande l’heure"""
        if event.key() == Qt.Key_Space:
            now = datetime.datetime.now()
            message = f"Il est {now.strftime('%H:%M:%S')}"
            self.show_message(message)
            try:
                self.engine.say(message)
                self.engine.runAndWait()
            except RuntimeError:
                # La boucle est déjà en cours d'exécution, ignorer l'erreur
                pass

    def show_message(self, texte):
        msg = QGraphicsTextItem(texte)
        msg.setDefaultTextColor(Qt.yellow)
        msg.setFont(QFont("Arial", 18, QFont.Bold))
        msg.setPos(200, 400)
        self.scene.addItem(msg)

        # Message disparaît après 3s
        QTimer.singleShot(3000, lambda: self.scene.removeItem(msg))


# ============================
#   Lancement
# ============================

def main():
    app = QApplication(sys.argv)
    w = Horloge()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
