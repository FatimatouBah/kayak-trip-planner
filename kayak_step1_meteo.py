import time
import requests
import pandas as pd

# ----------------------------------------------------------------
# CONFIGURATION - a completer
# ----------------------------------------------------------------
OPENWEATHER_API_KEY = "91151b9cfde6999722767fad37971e7d"  # <-- remplace par ta cle OpenWeatherMap

CITIES = [
    "Mont Saint Michel", "St Malo", "Bayeux", "Le Havre", "Rouen",
    "Paris", "Amiens", "Lille", "Strasbourg", "Chateau du Haut Koenigsbourg",
    "Colmar", "Eguisheim", "Besancon", "Dijon", "Annecy",
    "Grenoble", "Lyon", "Gorges du Verdon", "Bormes les Mimosas", "Cassis",
    "Marseille", "Aix en Provence", "Avignon", "Uzes", "Nimes",
    "Aigues Mortes", "Saintes Maries de la mer", "Collioure", "Carcassonne",
    "Ariege", "Toulouse", "Montauban", "Biarritz", "Bayonne", "La Rochelle",
]

# ----------------------------------------------------------------
# ETAPE 1 : Geolocalisation via Nominatim
# ----------------------------------------------------------------
def get_coordinates(city_name: str) -> dict | None:
    """Recupere latitude/longitude d'une ville via l'API Nominatim (OpenStreetMap)."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": city_name + ", France", "format": "json", "limit": 1}
    # Nominatim exige un User-Agent identifiable dans les headers
    headers = {"User-Agent": "kayak-jedha-project/1.0 (etudiante Jedha)"}

    response = requests.get(url, params=params, headers=headers, timeout=10)
    response.raise_for_status()
    results = response.json()

    if not results:
        print(f"  [ATTENTION] Aucune coordonnee trouvee pour : {city_name}")
        return None

    return {
        "city": city_name,
        "latitude": float(results[0]["lat"]),
        "longitude": float(results[0]["lon"]),
    }


def build_coordinates_dataframe(cities: list[str]) -> pd.DataFrame:
    """Boucle sur toutes les villes, avec une pause pour respecter Nominatim (max 1 req/s)."""
    rows = []
    for i, city in enumerate(cities, start=1):
        print(f"[{i}/{len(cities)}] Geolocalisation de {city}...")
        coords = get_coordinates(city)
        if coords:
            rows.append(coords)
        time.sleep(1)  # Nominatim impose max 1 requete par seconde
    return pd.DataFrame(rows)


# ----------------------------------------------------------------
# ETAPE 2 : Meteo via OpenWeatherMap (5 day / 3 hour forecast - gratuit)
# ----------------------------------------------------------------
def get_weather_forecast(lat: float, lon: float) -> dict:
    """
    Recupere les previsions sur 5 jours et calcule :
    - la temperature moyenne prevue
    - le volume de pluie total prevu
    - la probabilite de pluie moyenne
    """
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
        "lang": "fr",
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    temps = [entry["main"]["temp"] for entry in data["list"]]
    pops = [entry.get("pop", 0) for entry in data["list"]]  # probabilite de pluie (0 a 1)
    rain_volumes = [entry.get("rain", {}).get("3h", 0) for entry in data["list"]]

    return {
        "temp_moyenne": sum(temps) / len(temps),
        "temp_max": max(temps),
        "proba_pluie_moyenne": sum(pops) / len(pops),
        "volume_pluie_total_mm": sum(rain_volumes),
    }


def enrich_with_weather(df: pd.DataFrame) -> pd.DataFrame:
    """Ajoute les colonnes meteo a chaque ligne du DataFrame de villes."""
    weather_rows = []
    for i, row in df.iterrows():
        print(f"[{i+1}/{len(df)}] Meteo pour {row['city']}...")
        weather = get_weather_forecast(row["latitude"], row["longitude"])
        weather_rows.append(weather)
        time.sleep(1)  # petite pause de courtoisie sur l'API gratuite

    weather_df = pd.DataFrame(weather_rows)
    return pd.concat([df.reset_index(drop=True), weather_df], axis=1)


# ----------------------------------------------------------------
# ETAPE 3 : Score meteo + sauvegarde
# ----------------------------------------------------------------
def main():
    print("=== Etape 1/3 : Geolocalisation des villes ===")
    df = build_coordinates_dataframe(CITIES)

    print("\n=== Etape 2/3 : Recuperation meteo ===")
    df = enrich_with_weather(df)

    print("\n=== Etape 3/3 : Calcul du score meteo et sauvegarde ===")
    # Score simple : temperature elevee = bon point, pluie = mauvais point
    # Libre a toi d'ajuster la ponderation selon ce que TU juges important
    df["score_meteo"] = df["temp_moyenne"] - (df["volume_pluie_total_mm"] * 2)

    # Identifiant unique par ville (necessaire pour la suite du projet : hotels lies a une ville)
    df.insert(0, "id", range(1, len(df) + 1))

    df = df.sort_values("score_meteo", ascending=False).reset_index(drop=True)

    output_path = "villes_meteo.csv"
    df.to_csv(output_path, index=False)
    print(f"\nFichier sauvegarde : {output_path}")
    print(f"\nTop 5 des villes avec la meilleure meteo prevue :")
    print(df[["city", "temp_moyenne", "volume_pluie_total_mm", "score_meteo"]].head())


if __name__ == "__main__":
    main()
