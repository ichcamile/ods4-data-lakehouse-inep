"""
Testes da camada Silver.
Valida a estrutura, tipagem e integridade dos dados normalizados.
"""
import pytest
import pandas as pd


def test_silver_anos_disponiveis(silver_path):
    """Verifica que existem partições de anos na camada Silver."""
    parquets = sorted(silver_path.glob("ano=*/microdados_escola.parquet"))
    assert len(parquets) > 0, (
        f"Nenhum Parquet encontrado em {silver_path}. "
        "Execute: python -m src.jobs.silver.bronze_to_silver"
    )


def test_silver_colunas_normalizadas(silver_path):
    """Verifica que as colunas estão em snake_case e sem prefixos originais (NU_, CO_, etc)."""
    parquet = next(silver_path.glob("ano=*/microdados_escola.parquet"), None)
    if parquet is None:
        pytest.skip("Camada Silver não disponível.")

    df = pd.read_parquet(parquet)
    colunas_obrigatorias = [
        "ano_censo", "cod_escola", "nome_escola", "uf_sigla",
        "nome_municipio", "tp_dependencia", "qt_matriculas_total",
        "qt_docentes_total", "qt_turmas_total",
    ]
    faltando = [c for c in colunas_obrigatorias if c not in df.columns]
    assert faltando == [], f"Colunas obrigatórias ausentes na Silver: {faltando}"


def test_silver_sem_colunas_originais(silver_path):
    """Verifica que não há colunas com prefixos originais do INEP (NU_, NO_, CO_)."""
    parquet = next(silver_path.glob("ano=*/microdados_escola.parquet"), None)
    if parquet is None:
        pytest.skip("Camada Silver não disponível.")

    df = pd.read_parquet(parquet)
    prefixos_originais = ("NU_", "NO_", "CO_", "SG_", "TP_", "IN_", "QT_", "DS_")
    cols_originais = [c for c in df.columns if c.startswith(prefixos_originais)]
    assert cols_originais == [], f"Colunas com prefixo original encontradas: {cols_originais}"


def test_silver_tipos_corretos(silver_path):
    """Verifica que colunas numéricas têm tipo inteiro."""
    parquet = next(silver_path.glob("ano=2024/microdados_escola.parquet"), None)
    if parquet is None:
        pytest.skip("Silver 2024 não disponível.")

    df = pd.read_parquet(parquet)
    for col in ["qt_matriculas_total", "qt_docentes_total", "qt_turmas_total"]:
        assert pd.api.types.is_integer_dtype(df[col]), (
            f"Coluna {col} deveria ser inteiro, mas é {df[col].dtype}"
        )


def test_silver_sem_nulos_em_chaves(silver_path):
    """Verifica que as colunas-chave não têm nulos."""
    parquet = next(silver_path.glob("ano=2024/microdados_escola.parquet"), None)
    if parquet is None:
        pytest.skip("Silver 2024 não disponível.")

    df = pd.read_parquet(parquet)
    for col in ["cod_escola", "ano_censo"]:
        nulos = df[col].isna().sum()
        assert nulos == 0, f"Coluna {col} tem {nulos} nulos."
