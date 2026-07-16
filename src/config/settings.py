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

# ---------------------------------------------------------------------------
# Auto-detecção do Databricks
#
# O Databricks define a variável DATABRICKS_RUNTIME_VERSION no ambiente.
# Quando detectado, os caminhos padrão apontam para /dbfs/ — o sistema de
# arquivos distribuído que suporta arquivos grandes (sem limite de 10 MB).
#
# ⚠️  O Workspace (/Workspace/...) tem limite de 10 MB por arquivo.
#     Use sempre /dbfs/ ou Unity Catalog Volumes para dados do pipeline.
# ---------------------------------------------------------------------------
_DATABRICKS = (
    "DATABRICKS_RUNTIME_VERSION" in os.environ or 
    str(BASE_DIR).startswith("/Workspace/") or
    str(BASE_DIR).startswith("/dbfs/")
)
if _DATABRICKS:
    _DEFAULT_BRONZE = "/dbfs/FileStore/lakehouse_inep/bronze"
    _DEFAULT_SILVER = "/dbfs/FileStore/lakehouse_inep/silver"
    _DEFAULT_GOLD   = "/dbfs/FileStore/lakehouse_inep/gold"
    _DEFAULT_RAW    = "/dbfs/FileStore/lakehouse_inep/raw"
else:
    _DEFAULT_RAW    = str(BASE_DIR / "data" / "raw")
    _DEFAULT_BRONZE = str(BASE_DIR / "data" / "bronze")
    _DEFAULT_SILVER = str(BASE_DIR / "data" / "silver")
    _DEFAULT_GOLD   = str(BASE_DIR / "data" / "gold")

# Caminhos finais — variáveis de ambiente sempre têm precedência
RAW_DATA_PATH    = os.getenv("RAW_DATA_PATH",    _DEFAULT_RAW)
BRONZE_DATA_PATH = os.getenv("BRONZE_DATA_PATH", _DEFAULT_BRONZE)
SILVER_DATA_PATH = os.getenv("SILVER_DATA_PATH", _DEFAULT_SILVER)
GOLD_DATA_PATH   = os.getenv("GOLD_DATA_PATH",   _DEFAULT_GOLD)
