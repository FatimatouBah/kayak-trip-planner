import pandas as pd
import plotly.express as px

# ----------------------------------------------------------------
# Chargement des donnees
# ----------------------------------------------------------------
df = pd.read_csv("villes_meteo.csv")

# Le CSV est deja trie par score_meteo decroissant (fait a l'etape 1)
top5 = df.head(5).copy()

print("Top 5 des destinations selon la meteo :")
print(top5[["city", "temp_moyenne", "volume_pluie_total_mm", "score_meteo"]])

# ----------------------------------------------------------------
# Carte interactive
# ----------------------------------------------------------------
fig = px.scatter_mapbox(
    top5,
    lat="latitude",
    lon="longitude",
    hover_name="city",
    hover_data={
        "temp_moyenne": ":.1f",
        "volume_pluie_total_mm": ":.1f",
        "score_meteo": ":.1f",
        "latitude": False,
        "longitude": False,
    },
    color="score_meteo",
    size="score_meteo",
    color_continuous_scale=px.colors.sequential.Sunset,
    size_max=30,
    zoom=4.5,
    center={"lat": 46.5, "lon": 2.5},  # centre approximatif de la France
    title="Top 5 des destinations - Meilleure meteo prevue (5 prochains jours)",
)

fig.update_layout(
    mapbox_style="open-street-map",  # gratuit, ne necessite pas de token Mapbox
    margin={"r": 0, "t": 40, "l": 0, "b": 0},
)

# Sauvegarde en fichier HTML interactif (a ouvrir dans le navigateur)
fig.write_html("top5_destinations_map.html")
print("\nCarte sauvegardee : top5_destinations_map.html")

# Affiche aussi la carte directement si lance depuis un notebook / script local
fig.show()
