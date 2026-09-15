import boto3
import pandas as pd

BUCKET_NAME = "kayak-project-bahfa-2026"  # remplace par ton nom de bucket exact
REGION = "eu-west-3"
OUTPUT_FILE = "kayak_data_enrichi.csv"

# ----------------------------------------------------------------
# Etape 1 : Fusion des donnees
# ----------------------------------------------------------------
df_villes = pd.read_csv("villes_meteo.csv")
df_hotels = pd.read_csv("hotels.csv")

# On renomme "id" en "city_id" cote villes pour que la jointure soit explicite
df_villes = df_villes.rename(columns={"id": "city_id"})

# Jointure : chaque ligne = un hotel, avec les infos meteo de sa ville
df_enrichi = df_hotels.merge(
    df_villes,
    on="city_id",
    how="left",
    suffixes=("_hotel", "_ville"),
)

df_enrichi.to_csv(OUTPUT_FILE, index=False)
print(f"Fichier enrichi cree : {OUTPUT_FILE} ({len(df_enrichi)} lignes, {len(df_enrichi.columns)} colonnes)")
print("\nApercu :")
print(df_enrichi.head(3))

# ----------------------------------------------------------------
# Etape 2 : Upload vers S3
# ----------------------------------------------------------------
s3 = boto3.client("s3", region_name=REGION)

print(f"\nUpload de {OUTPUT_FILE} vers s3://{BUCKET_NAME}/{OUTPUT_FILE} ...")
s3.upload_file(OUTPUT_FILE, BUCKET_NAME, OUTPUT_FILE)
print("Upload termine avec succes !")

# Verification : on liste le contenu du bucket pour confirmer
print(f"\nContenu actuel du bucket s3://{BUCKET_NAME} :")
response = s3.list_objects_v2(Bucket=BUCKET_NAME)
for obj in response.get("Contents", []):
    print(f"  - {obj['Key']} ({obj['Size']} octets)")
