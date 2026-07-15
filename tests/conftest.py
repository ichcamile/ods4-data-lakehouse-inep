import pytest
import pandas as pd
from pathlib import Path


@pytest.fixture(scope="session")
def gold_path():
    """Caminho para a camada Gold do projeto."""
    base = Path(__file__).resolve().parent.parent
    return base / "data" / "gold"


@pytest.fixture(scope="session")
def silver_path():
    """Caminho para a camada Silver do projeto."""
    base = Path(__file__).resolve().parent.parent
    return base / "data" / "silver" / "microdados_escola"


@pytest.fixture(scope="session")
def bronze_path():
    """Caminho para a camada Bronze do projeto."""
    base = Path(__file__).resolve().parent.parent
    return base / "data" / "bronze"
