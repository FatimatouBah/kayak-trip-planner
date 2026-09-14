# Projet Kayak — Plan your trip with Kayak

Pipeline de données complet réalisé dans le cadre de la formation Jedha, pour recommander à Kayak les meilleures destinations de vacances en France selon la météo et les hébergements disponibles.

## 🎯 Objectif

Construire une application capable de recommander des destinations de voyage en France, en s'appuyant sur des données réelles de météo et d'hôtellerie plutôt que sur des critères subjectifs.

## 📊 Données

- 35 villes les plus visitées de France (source : OneWeekIn.com)
- Coordonnées GPS via l'API **Nominatim** (OpenStreetMap)
- Prévisions météo via l'API **OpenWeatherMap**
- Données hôtelières scrapées sur **Booking.com** (nom, note, description, coordonnées)

## 🛠️ Outils

- **Python** (pandas, requests, Selenium, Plotly, boto3, SQLAlchemy)
- **Amazon S3** — data lake (stockage du CSV enrichi)
- **Amazon RDS (PostgreSQL)** — data warehouse

## 🏗️ Architecture du pipeline

1. **Extraction** — géolocalisation des villes + météo (Nominatim, OpenWeatherMap) et scraping hôtels (Selenium + Booking.com)
2. **Fusion** — jointure météo/hôtels sur l'identifiant de chaque ville
3. **Data Lake** — dépôt du CSV enrichi sur Amazon S3
4. **Data Warehouse** — chargement structuré dans une base PostgreSQL sur Amazon RDS

## 📁 Contenu du repo

| Fichier | Description |
|---|---|
| `kayak_step1_meteo.py` | Géolocalisation des 35 villes + récupération météo |
| `kayak_step2_carte_top5.py` | Carte Plotly des 5 meilleures destinations |
| `kayak_step3_scraping_booking.py` | Scraping des hôtels sur Booking.com |
| `kayak_step4_carte_top20_hotels.py` | Carte Plotly des 20 meilleurs hôtels |
| `kayak_step5_fusion_upload_s3.py` | Fusion des données et upload vers S3 |
| `kayak_step6_etl_s3_to_rds.py` | Chargement des données de S3 vers RDS PostgreSQL |
| `villes_meteo.csv` | Données météo des 35 villes |
| `hotels.csv` | 100 hôtels extraits sur les 5 meilleures destinations |
| `top5_destinations_map.html` | Carte interactive des 5 meilleures destinations |
| `top20_hotels_map.html` | Carte interactive des 20 meilleurs hôtels |
| `Projet_Kayak_Recapitulatif.docx` | Document de présentation du projet |
| `Projet_Kayak_Presentation.pptx` | Slides de présentation |

## 🏆 Résultats clés

Les 5 meilleures destinations selon le score météo (température élevée, peu de pluie prévue) : **Collioure, Nîmes, Carcassonne, Marseille, Aigues-Mortes**.
