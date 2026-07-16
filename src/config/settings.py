import os
from pathlib import Path
from dotenv import load_dotenv

# Load env variables from .env if present
load_dotenv()

# Root directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# App metadata
APP_NAME = os.getenv("APP_NAME", "ODS4-Lakehouse-INEP")

# Environment configurations (local, dev, prod)
ENV = os.getenv("ENVIRONMENT", "local")

_DEFAULT_RAW    = str(BASE_DIR / "data" / "raw")
_DEFAULT_BRONZE = str(BASE_DIR / "data" / "bronze")
_DEFAULT_SILVER = str(BASE_DIR / "data" / "silver")
_DEFAULT_GOLD   = str(BASE_DIR / "data" / "gold")

# Caminhos finais — variáveis de ambiente sempre têm precedência
RAW_DATA_PATH    = os.getenv("RAW_DATA_PATH",    _DEFAULT_RAW)
BRONZE_DATA_PATH = os.getenv("BRONZE_DATA_PATH", _DEFAULT_BRONZE)
SILVER_DATA_PATH = os.getenv("SILVER_DATA_PATH", _DEFAULT_SILVER)
GOLD_DATA_PATH   = os.getenv("GOLD_DATA_PATH",   _DEFAULT_GOLD)
