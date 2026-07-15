"""
Testes da camada Bronze.
Verifica que os arquivos CSV foram extraídos corretamente para data/bronze/.
"""
import pytest
from pathlib import Path


def test_bronze_anos_disponiveis(bronze_path):
    """Verifica que existem partições de anos na camada Bronze."""
    ano_dirs = sorted(bronze_path.glob("ano=*"))
    assert len(ano_dirs) > 0, (
        f"Nenhum diretório ano=* encontrado em {bronze_path}. "
        "Execute: python -m src.jobs.bronze.zip_to_file"
    )


def test_bronze_csvs_presentes(bronze_path):
    """Verifica que cada partição de ano contém ao menos 1 CSV.
    
    Nota: ano=2020 é excluído pois o INEP não publicou os microdados de 2020.
    """
    ANOS_SEM_DADOS = {"ano=2020"}
    ano_dirs = sorted(bronze_path.glob("ano=*"))
    vazios = [
        d.name for d in ano_dirs
        if not list(d.glob("*.csv")) and d.name not in ANOS_SEM_DADOS
    ]
    assert vazios == [], f"Diretórios sem CSV: {vazios}"


def test_bronze_2024_header(bronze_path):
    """Verifica que o CSV de 2024 contém as colunas essenciais do Censo Escolar."""
    import pandas as pd
    csv_2024 = bronze_path / "ano=2024" / "microdados_ed_basica_2024.csv"
    if not csv_2024.exists():
        pytest.skip("Arquivo Bronze 2024 não disponível.")

    df = pd.read_csv(csv_2024, sep=";", encoding="latin-1", nrows=1)
    colunas_essenciais = ["NU_ANO_CENSO", "CO_ENTIDADE", "NO_ENTIDADE", "QT_MAT_BAS"]
    faltando = [c for c in colunas_essenciais if c not in df.columns]
    assert faltando == [], f"Colunas ausentes no Bronze 2024: {faltando}"
