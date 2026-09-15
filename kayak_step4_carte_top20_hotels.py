"""
Projet Kayak - Etape 4 : Carte des Top 20 hotels
===================================================
Ce script lit hotels.csv (genere par kayak_step3_scraping_booking.py),
selectionne les 20 hotels les mieux notes (tous villes confondues),
et affiche une carte interactive avec Plotly.
"""

import pandas as pd
import plotly.express as px

# ----------------------------------------------------------------
# Chargement et selection du top 20
# ----------------------------------------------------------------
df = pd.read_csv("hotels.csv")

# On retire les hotels sans note ou sans coordonnees (impossibles a classer/afficher)
df_valid = df.dropna(subset=["score", "latitude", "longitude"])

top20 = df_valid.sort_values("score", ascending=False).head(20).copy()

print(f"{len(df_valid)} hotels notes et geolocalises sur {len(df)} au total")
print("\nTop 20 des hotels les mieux notes :")
print(top20[["hotel_name", "city", "score"]].to_string(index=False))

# ----------------------------------------------------------------
# Carte interactive
# ----------------------------------------------------------------
fig = px.scatter_mapbox(
    top20,
    lat="latitude",
    lon="longitude",
    hover_name="hotel_name",
    hover_data={
        "city": True,
        "score": ":.1f",
        "latitude": False,
        "longitude": False,
    },
    color="city",
    size="score",
    size_max=20,
    zoom=5.5,
    center={"lat": 43.5, "lon": 3.5},  # centre approximatif sur le sud de la France
    title="Top 20 des hotels les mieux notes (sur les 5 meilleures destinations meteo)",
)

fig.update_layout(
    mapbox_style="open-street-map",
    margin={"r": 0, "t": 40, "l": 0, "b": 0},
)

fig.write_html("top20_hotels_map.html")
print("\nCarte sauvegardee : top20_hotels_map.html")

fig.show()
