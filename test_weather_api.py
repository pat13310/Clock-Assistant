import requests
import json

def test_weather_data(city="Paris"):
    """
    Teste la récupération des données météo pour une ville donnée.
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
        data = response.json()
        
        # Afficher la structure des données
        print("Structure des données de l'API:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # Extraire les informations spécifiques
        print("\nInformations spécifiques:")
        print(f"Température: {data['main']['temp']}°C")
        print(f"Pression: {data['main']['pressure']} hPa")
        print(f"Vitesse du vent: {data['wind']['speed']} m/s")
        
        return data
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération des données météo: {e}")
        return None

if __name__ == "__main__":
    test_weather_data()