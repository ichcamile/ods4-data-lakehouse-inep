"""
Testes da camada Gold.
Valida a existência, estrutura e integridade das tabelas analíticas.
"""
import pytest
import pandas as pd


def test_gold_tabelas_existem(gold_path):
    """Verifica que as 3 tabelas Gold foram geradas."""
    tabelas = [
        "dim_escola.parquet",
        "fct_matriculas_por_escola_ano.parquet",
        "fct_docentes_turmas_por_escola_ano.parquet",
    ]
    faltando = [t for t in tabelas if not (gold_path / t).exists()]
    assert faltando == [], (
        f"Tabelas Gold ausentes: {faltando}. "
        "Execute: python -m src.jobs.gold.silver_to_gold"
    )


def test_gold_dim_escola_chave_unica(gold_path):
    """Verifica que dim_escola tem registros únicos por cod_escola."""
    p = gold_path / "dim_escola.parquet"
    if not p.exists():
        pytest.skip("dim_escola.parquet não disponível.")

    df = pd.read_parquet(p)
    duplicatas = df["cod_escola"].duplicated().sum()
    assert duplicatas == 0, f"dim_escola tem {duplicatas} cod_escola duplicados."


def test_gold_dim_escola_colunas(gold_path):
    """Verifica colunas obrigatórias na dim_escola."""
    p = gold_path / "dim_escola.parquet"
    if not p.exists():
        pytest.skip("dim_escola.parquet não disponível.")

    df = pd.read_parquet(p)
    obrigatorias = [
        "cod_escola", "nome_escola", "uf_sigla", "nome_municipio",
        "nome_regiao", "tp_dependencia", "desc_dependencia",
        "tp_localizacao", "desc_localizacao", "ano_referencia",
    ]
    faltando = [c for c in obrigatorias if c not in df.columns]
    assert faltando == [], f"Colunas ausentes em dim_escola: {faltando}"


def test_gold_fct_matriculas_chave(gold_path):
    """Verifica que fct_matriculas tem no máximo 1 registro por (cod_escola, ano_censo)."""
    p = gold_path / "fct_matriculas_por_escola_ano.parquet"
    if not p.exists():
        pytest.skip("fct_matriculas_por_escola_ano.parquet não disponível.")

    df = pd.read_parquet(p)
    duplicatas = df.duplicated(subset=["cod_escola", "ano_censo"]).sum()
    assert duplicatas == 0, (
        f"fct_matriculas tem {duplicatas} pares (cod_escola, ano_censo) duplicados."
    )


def test_gold_fct_matriculas_sem_negativos(gold_path):
    """Verifica que não há valores negativos nas colunas de quantidade de matrículas."""
    p = gold_path / "fct_matriculas_por_escola_ano.parquet"
    if not p.exists():
        pytest.skip("fct_matriculas_por_escola_ano.parquet não disponível.")

    df = pd.read_parquet(p)
    qt_cols = [c for c in df.columns if c.startswith("qt_")]
    for col in qt_cols:
        negativos = (df[col] < 0).sum()
        assert negativos == 0, f"Coluna {col} tem {negativos} valores negativos."


def test_gold_fct_docentes_anos_cobertos(gold_path):
    """Verifica que fct_docentes_turmas cobre pelo menos 10 anos."""
    p = gold_path / "fct_docentes_turmas_por_escola_ano.parquet"
    if not p.exists():
        pytest.skip("fct_docentes_turmas_por_escola_ano.parquet não disponível.")

    df = pd.read_parquet(p)
    n_anos = df["ano_censo"].nunique()
    assert n_anos >= 10, f"fct_docentes_turmas cobre apenas {n_anos} anos (esperado ≥10)."
