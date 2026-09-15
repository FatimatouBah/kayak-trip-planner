import boto3
import pandas as pd
from sqlalchemy import create_engine

# ----------------------------------------------------------------
# CONFIGURATION - a completer avec TES informations
# ----------------------------------------------------------------
BUCKET_NAME = "kayak-project-bahfa-2026"
S3_KEY = "kayak_data_enrichi.csv"
REGION = "eu-west-3"

# Recupere ces infos dans la console RDS, sur la page de ta base "kayak-db" :
RDS_ENDPOINT = "kayak-db.c32qo0mgcw97.eu-west-3.rds.amazonaws.com"  # "Endpoint" affiche dans RDS
RDS_PORT = 5432
RDS_DB_NAME = "postgres"          # nom de base par defaut, sauf si tu en as specifie un autre
RDS_USER = "postgres"             # le "Master username" que tu as choisi
RDS_PASSWORD = "ThiernoFatou44"  # le "Master password" que tu as choisi

TABLE_NAME = "kayak_destinations"

# ----------------------------------------------------------------
# Etape 1 : Telechargement depuis S3
# ----------------------------------------------------------------
print(f"Telechargement de s3://{BUCKET_NAME}/{S3_KEY} ...")
s3 = boto3.client("s3", region_name=REGION)
s3.download_file(BUCKET_NAME, S3_KEY, "temp_kayak_data.csv")

df = pd.read_csv("temp_kayak_data.csv")
print(f"{len(df)} lignes chargees depuis S3")

# ----------------------------------------------------------------
# Etape 2 : Connexion a RDS et chargement
# ----------------------------------------------------------------
connection_string = (
    f"postgresql://{RDS_USER}:{RDS_PASSWORD}@{RDS_ENDPOINT}:{RDS_PORT}/{RDS_DB_NAME}"
)
engine = create_engine(connection_string)

print(f"Connexion a {RDS_ENDPOINT} et ecriture dans la table '{TABLE_NAME}'...")
df.to_sql(TABLE_NAME, engine, if_exists="replace", index=False)
print("Chargement termine avec succes !")

# ----------------------------------------------------------------
# Etape 3 : Verification
# ----------------------------------------------------------------
with engine.connect() as conn:
    result = conn.exec_driver_sql(f"SELECT COUNT(*) FROM {TABLE_NAME}")
    count = result.scalar()
    print(f"\nVerification : {count} lignes presentes dans la table '{TABLE_NAME}' sur RDS")

    preview = pd.read_sql(f"SELECT city_hotel, hotel_name, score, temp_moyenne FROM {TABLE_NAME} LIMIT 5", conn)
    print("\nApercu des donnees dans la base :")
    print(preview)
