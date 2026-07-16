import sys
import pandas as pd
from pathlib import Path

# Bootstrap do sys.path
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.config import settings
from src.utils.logger import get_logger

logger = get_logger("silver_to_gold")

# ---------------------------------------------------------------------------
# Descrições legíveis para os valores de tipo/categoria
# ---------------------------------------------------------------------------
DEPENDENCIA_MAP = {
    1: "Federal",
    2: "Estadual",
    3: "Municipal",
    4: "Privada",
    -1: "Não informado",
}

LOCALIZACAO_MAP = {
    1: "Urbana",
    2: "Rural",
    -1: "Não informado",
}

SITUACAO_MAP = {
    1: "Em atividade",
    2: "Paralisada",
    3: "Extinta no ano do Censo",
    4: "Extinção em anos anteriores",
    -1: "Não informado",
}

CATEGORIA_PRIVADA_MAP = {
    1: "Particular",
    2: "Comunitária",
    3: "Confessional",
    4: "Filantrópica",
    -1: "Não se aplica",
}


def _read_silver(silver_path: Path) -> pd.DataFrame:
    """Lê todos os parquets da Silver e une em um único DataFrame."""
    parquet_files = sorted(silver_path.glob("ano=*/microdados_escola.parquet"))

    if not parquet_files:
        raise FileNotFoundError(
            f"Nenhum arquivo parquet encontrado em {silver_path}. "
            "Execute primeiro o pipeline Bronze → Silver."
        )

    dfs = []
    for f in parquet_files:
        df = pd.read_parquet(f, engine="pyarrow")
        dfs.append(df)
        logger.info(f"  Lido: {f} — {len(df):,} linhas")

    df_all = pd.concat(dfs, ignore_index=True)
    logger.info(f"Total Silver carregado: {len(df_all):,} registros, {df_all['ano_censo'].nunique()} anos")
    return df_all


def _build_dim_escola(df: pd.DataFrame) -> pd.DataFrame:
    """
    Dimensão de escolas: dados identificadores únicos por escola.
    Usa o último registro disponível para cada cod_escola.
    """
    logger.info("Construindo dim_escola...")

    dim_cols = [
        "cod_escola", "nome_escola",
        "cod_regiao", "nome_regiao",
        "cod_uf", "uf_sigla", "nome_uf",
        "cod_municipio", "nome_municipio",
        "tp_dependencia", "tp_localizacao",
        "tp_situacao_funcionamento", "tp_categoria_escola_privada",
        "in_regular", "in_eja", "in_especial", "in_profissional",
        "ano_censo",
    ]

    # Seleciona apenas colunas disponíveis
    available = [c for c in dim_cols if c in df.columns]
    df_dim = df[available].copy()

    # Último registro por escola (ano mais recente)
    df_dim = (
        df_dim
        .sort_values("ano_censo", ascending=False)
        .drop_duplicates(subset=["cod_escola"], keep="first")
        .rename(columns={"ano_censo": "ano_referencia"})
        .reset_index(drop=True)
    )

    # Labels legíveis
    if "tp_dependencia" in df_dim.columns:
        df_dim["desc_dependencia"] = df_dim["tp_dependencia"].map(DEPENDENCIA_MAP).fillna("Não informado")

    if "tp_localizacao" in df_dim.columns:
        df_dim["desc_localizacao"] = df_dim["tp_localizacao"].map(LOCALIZACAO_MAP).fillna("Não informado")

    if "tp_situacao_funcionamento" in df_dim.columns:
        df_dim["desc_situacao"] = df_dim["tp_situacao_funcionamento"].map(SITUACAO_MAP).fillna("Não informado")

    if "tp_categoria_escola_privada" in df_dim.columns:
        df_dim["desc_categoria_privada"] = df_dim["tp_categoria_escola_privada"].map(CATEGORIA_PRIVADA_MAP).fillna("Não informado")

    logger.info(f"  dim_escola: {len(df_dim):,} escolas únicas")
    return df_dim


def _build_fct_matriculas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fato: matrículas por escola/ano desagregadas por nível, sexo e raça/cor.
    Um registro por (cod_escola, ano_censo).
    """
    logger.info("Construindo fct_matriculas_por_escola_ano...")

    mat_cols = [
        "cod_escola", "ano_censo",
        "qt_matriculas_total",
        "qt_mat_infantil", "qt_mat_creche", "qt_mat_pre_escola",
        "qt_mat_fundamental", "qt_mat_fund_anos_iniciais", "qt_mat_fund_anos_finais",
        "qt_mat_medio",
        "qt_mat_profissional", "qt_mat_prof_tecnico",
        "qt_mat_eja", "qt_mat_eja_fundamental", "qt_mat_eja_medio",
        "qt_mat_especial",
        "qt_mat_feminino", "qt_mat_masculino",
        "qt_mat_branca", "qt_mat_preta", "qt_mat_parda",
        "qt_mat_amarela", "qt_mat_indigena",
    ]

    available = [c for c in mat_cols if c in df.columns]
    df_fct = df[available].copy()

    # Garante unicidade por (cod_escola, ano_censo) — em caso de duplicatas, soma
    df_fct = (
        df_fct
        .groupby(["cod_escola", "ano_censo"], as_index=False)
        .sum(numeric_only=True)
    )

    logger.info(f"  fct_matriculas: {len(df_fct):,} registros")
    return df_fct


def _build_fct_docentes_turmas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fato: docentes, turmas e infraestrutura por escola/ano.
    Um registro por (cod_escola, ano_censo).
    """
    logger.info("Construindo fct_docentes_turmas_por_escola_ano...")

    doc_cols = [
        "cod_escola", "ano_censo",
        "qt_docentes_total", "qt_doc_infantil", "qt_doc_fundamental",
        "qt_doc_medio", "qt_doc_profissional", "qt_doc_eja", "qt_doc_especial",
        "qt_turmas_total", "qt_tur_infantil", "qt_tur_fundamental",
        "qt_tur_medio", "qt_tur_eja", "qt_tur_especial",
        "qt_salas_utilizadas",
        "in_agua_potavel", "in_energia_rede_publica", "in_internet",
        "in_internet_alunos", "in_biblioteca", "in_laboratorio_info",
        "in_quadra_esportes", "in_alimentacao",
    ]

    available = [c for c in doc_cols if c in df.columns]
    df_fct = df[available].copy()

    # Indicadores: usar max (se algum registro do ano tem =1, escola tem)
    indicator_cols = [c for c in [
        "in_agua_potavel", "in_energia_rede_publica", "in_internet",
        "in_internet_alunos", "in_biblioteca", "in_laboratorio_info",
        "in_quadra_esportes", "in_alimentacao",
    ] if c in df_fct.columns]

    qty_cols = [c for c in doc_cols if c not in ["cod_escola", "ano_censo"] and c not in indicator_cols]

    agg_dict = {c: "sum" for c in qty_cols if c in df_fct.columns}
    agg_dict.update({c: "max" for c in indicator_cols})

    df_fct = (
        df_fct
        .groupby(["cod_escola", "ano_censo"], as_index=False)
        .agg(agg_dict)
    )

    logger.info(f"  fct_docentes_turmas: {len(df_fct):,} registros")
    return df_fct


def run():
    """
    Job Silver → Gold.
    Lê a camada Silver e gera 3 tabelas Gold em Parquet:
      - dim_escola
      - fct_matriculas_por_escola_ano
      - fct_docentes_turmas_por_escola_ano
    """
    silver_path = Path(settings.SILVER_DATA_PATH) / "microdados_escola"
    gold_path = Path(settings.GOLD_DATA_PATH)

    gold_path.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 60)
    logger.info("Iniciando pipeline Silver → Gold")
    logger.info(f"  Silver: {silver_path}")
    logger.info(f"  Gold:   {gold_path}")
    logger.info("=" * 60)

    # --- Leitura da Silver ---
    df_silver = _read_silver(silver_path)

    # --- Tabela 1: dim_escola ---
    df_dim = _build_dim_escola(df_silver)
    dim_path = gold_path / "dim_escola.parquet"
    df_dim.to_parquet(dim_path, index=False, engine="pyarrow")
    logger.info(f"  ✓ dim_escola gravada → {dim_path}")

    # --- Tabela 2: fct_matriculas_por_escola_ano ---
    df_mat = _build_fct_matriculas(df_silver)
    mat_path = gold_path / "fct_matriculas_por_escola_ano.parquet"
    df_mat.to_parquet(mat_path, index=False, engine="pyarrow")
    logger.info(f"  ✓ fct_matriculas_por_escola_ano gravada → {mat_path}")

    # --- Tabela 3: fct_docentes_turmas_por_escola_ano ---
    df_doc = _build_fct_docentes_turmas(df_silver)
    doc_path = gold_path / "fct_docentes_turmas_por_escola_ano.parquet"
    df_doc.to_parquet(doc_path, index=False, engine="pyarrow")
    logger.info(f"  ✓ fct_docentes_turmas_por_escola_ano gravada → {doc_path}")

    logger.info("=" * 60)
    logger.info("Pipeline Gold concluído com sucesso!")
    logger.info(f"  dim_escola:                    {len(df_dim):>10,} registros")
    logger.info(f"  fct_matriculas:                {len(df_mat):>10,} registros")
    logger.info(f"  fct_docentes_turmas:           {len(df_doc):>10,} registros")
    logger.info("=" * 60)


if __name__ == "__main__":
    run()
