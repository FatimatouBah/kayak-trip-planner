import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

NB_HOTELS_PAR_VILLE = 20
CHECKIN = "2026-10-15"   # adapte les dates si besoin
CHECKOUT = "2026-10-17"


def start_browser() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--lang=fr-FR")
    # Decommente la ligne suivante si tu veux que le navigateur ne s'affiche pas a l'ecran :
    # options.add_argument("--headless=new")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def scrape_hotels_for_city(driver: webdriver.Chrome, city: str, city_id: int) -> list[dict]:
    """Scrape jusqu'a NB_HOTELS_PAR_VILLE hotels Booking.com pour une ville donnee."""
    search_url = (
        "https://www.booking.com/searchresults.fr.html"
        f"?ss={city.replace(' ', '+')}"
        f"&checkin={CHECKIN}&checkout={CHECKOUT}"
        "&group_adults=2&no_rooms=1&group_children=0"
    )
    print(f"\n--- Scraping de {city} ---")
    driver.get(search_url)
    time.sleep(4)  # laisser la page charger

    # Fermer la popup de connexion / cookies si elle apparait (selecteurs a ajuster si besoin)
    try:
        driver.find_element(By.CSS_SELECTOR, "[aria-label='Refuser']").click()
    except Exception:
        pass
    try:
        driver.find_element(By.CSS_SELECTOR, "button[aria-label='Fermer']").click()
    except Exception:
        pass

    # Scroll pour charger davantage de resultats (Booking.com charge au scroll)
    for _ in range(6):
        driver.execute_script("window.scrollBy(0, 1000)")
        time.sleep(1)

    # Chaque carte hotel est dans un bloc avec ce data-testid (a verifier/adapter via F12)
    cards = driver.find_elements(By.CSS_SELECTOR, "[data-testid='property-card']")
    print(f"  {len(cards)} cartes d'hotel trouvees sur la page")

    hotels = []
    for card in cards[:NB_HOTELS_PAR_VILLE]:
        try:
            name = card.find_element(By.CSS_SELECTOR, "[data-testid='title']").text
        except Exception:
            name = None
        try:
            url = card.find_element(By.CSS_SELECTOR, "[data-testid='title-link']").get_attribute("href")
        except Exception:
            url = None
        try:
            score_text = card.find_element(By.CSS_SELECTOR, "[data-testid='review-score'] div").text
            score_match = re.search(r"[\d,.]+", score_text)
            score = float(score_match.group().replace(",", ".")) if score_match else None
        except Exception:
            score = None
        try:
            description = card.find_element(By.CSS_SELECTOR, "[data-testid='recommended-units']").text
        except Exception:
            description = None

        if name and url:
            hotels.append({
                "city_id": city_id,
                "city": city,
                "hotel_name": name,
                "url": url,
                "score": score,
                "description": description,
                # Booking n'affiche pas toujours lat/lon directement sur la page de resultats ;
                # on les recupere via la fiche detail si besoin (etape optionnelle plus bas)
                "latitude": None,
                "longitude": None,
            })

    print(f"  {len(hotels)} hotels extraits pour {city}")
    return hotels


def get_hotel_coordinates(driver: webdriver.Chrome, hotel_url: str) -> tuple[float, float] | tuple[None, None]:
    """Optionnel : va sur la page detail de l'hotel pour recuperer lat/lon precises."""
    try:
        driver.get(hotel_url)
        time.sleep(2)
        map_link = driver.find_element(By.CSS_SELECTOR, "a[data-atlas-latlng]")
        latlng = map_link.get_attribute("data-atlas-latlng")
        lat_str, lon_str = latlng.split(",")
        return float(lat_str), float(lon_str)
    except Exception:
        return None, None


def main():
    df_villes = pd.read_csv("villes_meteo.csv")
    top5 = df_villes.head(5)

    driver = start_browser()
    all_hotels = []

    try:
        for _, row in top5.iterrows():
            hotels = scrape_hotels_for_city(driver, row["city"], row["id"])
            all_hotels.extend(hotels)
            time.sleep(2)  # pause de courtoisie entre chaque ville

        # Etape optionnelle : recuperer les coordonnees precises de chaque hotel
        # (rallonge beaucoup le temps d'execution : ~2-3s par hotel)
        print("\n--- Recuperation des coordonnees precises des hotels ---")
        for hotel in all_hotels:
            lat, lon = get_hotel_coordinates(driver, hotel["url"])
            hotel["latitude"] = lat
            hotel["longitude"] = lon
            time.sleep(1)

    finally:
        driver.quit()

    df_hotels = pd.DataFrame(all_hotels)
    df_hotels.to_csv("hotels.csv", index=False)
    print(f"\nTermine ! {len(df_hotels)} hotels sauvegardes dans hotels.csv")


if __name__ == "__main__":
    main()
