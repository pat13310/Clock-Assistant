import requests
import json

class OpenWeather:
    def __init__(self, api_key, city="Paris"):
        self.api_key = api_key
        self.city = city
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        
    def get_weather_data(self):
        """
        Récupère les données météo pour une ville donnée.
        Utilise l'API OpenWeatherMap.
        """
        params = {
            "q": self.city,
            "appid": self.api_key,
            "units": "metric",  # Température en Celsius
            "lang": "fr"  # Description en français
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()  # Lève une exception pour les codes d'erreur HTTP
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la récupération des données météo: {e}")
            return None
            
    def get_weather_condition(self, weather_data):
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