import os
from pathlib import Path
from dotenv import load_dotenv

# Load env variables from .env if present
load_dotenv()

# Root directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# App metadata
APP_NAME = os.getenv("SPARK_APP_NAME", "ODS4-Lakehouse-INEP")

# Environment configurations (local, dev, prod)
ENV = os.getenv("ENVIRONMENT", "local")

# Medallion layers paths
# In a real environment, these would point to s3a://, abfss:// or gs://
RAW_DATA_PATH = os.getenv("RAW_DATA_PATH", str(BASE_DIR / "data" / "raw"))
BRONZE_DATA_PATH = os.getenv("BRONZE_DATA_PATH", str(BASE_DIR / "data" / "bronze"))
SILVER_DATA_PATH = os.getenv("SILVER_DATA_PATH", str(BASE_DIR / "data" / "silver"))
GOLD_DATA_PATH = os.getenv("GOLD_DATA_PATH", str(BASE_DIR / "data" / "gold"))

# Spark Master configuration
SPARK_MASTER = os.getenv("SPARK_MASTER", "local[*]")
