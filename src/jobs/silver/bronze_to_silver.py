import os
import sys
import glob
import pandas as pd
from pathlib import Path

# Bootstrap do sys.path
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.config import settings
from src.utils.logger import get_logger

logger = get_logger("bronze_to_silver")

# ---------------------------------------------------------------------------
# Mapeamento: coluna_original -> nome_silver
# Apenas colunas presentes na grande maioria dos anos do Censo Escolar.
# ---------------------------------------------------------------------------
COLUMN_RENAME_MAP = {
    "NU_ANO_CENSO":            "ano_censo",
    "CO_ENTIDADE":             "cod_escola",
    "NO_ENTIDADE":             "nome_escola",
    "CO_REGIAO":               "cod_regiao",
    "NO_REGIAO":               "nome_regiao",
    "CO_UF":                   "cod_uf",
    "SG_UF":                   "uf_sigla",
    "NO_UF":                   "nome_uf",
    "CO_MUNICIPIO":            "cod_municipio",
    "NO_MUNICIPIO":            "nome_municipio",
    "TP_DEPENDENCIA":          "tp_dependencia",
    "TP_LOCALIZACAO":          "tp_localizacao",
    "TP_SITUACAO_FUNCIONAMENTO": "tp_situacao_funcionamento",
    "TP_CATEGORIA_ESCOLA_PRIVADA": "tp_categoria_escola_privada",
    "IN_REGULAR":              "in_regular",
    "IN_EAD":                  "in_ead",
    "IN_INF":                  "in_infantil",
    "IN_FUND":                 "in_fundamental",
    "IN_MED":                  "in_medio",
    "IN_PROF":                 "in_profissional",
    "IN_EJA":                  "in_eja",
    "IN_ESP":                  "in_especial",
    # Matrículas
    "QT_MAT_BAS":              "qt_matriculas_total",
    "QT_MAT_INF":              "qt_mat_infantil",
    "QT_MAT_INF_CRE":          "qt_mat_creche",
    "QT_MAT_INF_PRE":          "qt_mat_pre_escola",
    "QT_MAT_FUND":             "qt_mat_fundamental",
    "QT_MAT_FUND_AI":          "qt_mat_fund_anos_iniciais",
    "QT_MAT_FUND_AF":          "qt_mat_fund_anos_finais",
    "QT_MAT_MED":              "qt_mat_medio",
    "QT_MAT_PROF":             "qt_mat_profissional",
    "QT_MAT_PROF_TEC":         "qt_mat_prof_tecnico",
    "QT_MAT_EJA":              "qt_mat_eja",
    "QT_MAT_EJA_FUND":         "qt_mat_eja_fundamental",
    "QT_MAT_EJA_MED":          "qt_mat_eja_medio",
    "QT_MAT_ESP":              "qt_mat_especial",
    "QT_MAT_BAS_FEM":          "qt_mat_feminino",
    "QT_MAT_BAS_MASC":         "qt_mat_masculino",
    "QT_MAT_BAS_BRANCA":       "qt_mat_branca",
    "QT_MAT_BAS_PRETA":        "qt_mat_preta",
    "QT_MAT_BAS_PARDA":        "qt_mat_parda",
    "QT_MAT_BAS_AMARELA":      "qt_mat_amarela",
    "QT_MAT_BAS_INDIGENA":     "qt_mat_indigena",
    # Docentes
    "QT_DOC_BAS":              "qt_docentes_total",
    "QT_DOC_INF":              "qt_doc_infantil",
    "QT_DOC_FUND":             "qt_doc_fundamental",
    "QT_DOC_MED":              "qt_doc_medio",
    "QT_DOC_PROF":             "qt_doc_profissional",
    "QT_DOC_EJA":              "qt_doc_eja",
    "QT_DOC_ESP":              "qt_doc_especial",
    # Turmas
    "QT_TUR_BAS":              "qt_turmas_total",
    "QT_TUR_INF":              "qt_tur_infantil",
    "QT_TUR_FUND":             "qt_tur_fundamental",
    "QT_TUR_MED":              "qt_tur_medio",
    "QT_TUR_EJA":              "qt_tur_eja",
    "QT_TUR_ESP":              "qt_tur_especial",
    # Infraestrutura
    "QT_SALAS_UTILIZADAS":     "qt_salas_utilizadas",
    "IN_AGUA_POTAVEL":         "in_agua_potavel",
    "IN_ENERGIA_REDE_PUBLICA": "in_energia_rede_publica",
    "IN_INTERNET":             "in_internet",
    "IN_INTERNET_ALUNOS":      "in_internet_alunos",
    "IN_BIBLIOTECA":           "in_biblioteca",
    "IN_LABORATORIO_INFORMATICA": "in_laboratorio_info",
    "IN_QUADRA_ESPORTES":      "in_quadra_esportes",
    "IN_ALIMENTACAO":          "in_alimentacao",
}

# Colunas de indicador (0/1) — preencher nulos com 0
INDICATOR_COLS = [
    "in_regular", "in_ead", "in_infantil", "in_fundamental", "in_medio",
    "in_profissional", "in_eja", "in_especial",
    "in_agua_potavel", "in_energia_rede_publica", "in_internet",
    "in_internet_alunos", "in_biblioteca", "in_laboratorio_info",
    "in_quadra_esportes", "in_alimentacao",
]

# Colunas numéricas de quantidade — preencher nulos com 0
QUANTITY_COLS = [
    "qt_matriculas_total", "qt_mat_infantil", "qt_mat_creche", "qt_mat_pre_escola",
    "qt_mat_fundamental", "qt_mat_fund_anos_iniciais", "qt_mat_fund_anos_finais",
    "qt_mat_medio", "qt_mat_profissional", "qt_mat_prof_tecnico",
    "qt_mat_eja", "qt_mat_eja_fundamental", "qt_mat_eja_medio", "qt_mat_especial",
    "qt_mat_feminino", "qt_mat_masculino",
    "qt_mat_branca", "qt_mat_preta", "qt_mat_parda", "qt_mat_amarela", "qt_mat_indigena",
    "qt_docentes_total", "qt_doc_infantil", "qt_doc_fundamental",
    "qt_doc_medio", "qt_doc_profissional", "qt_doc_eja", "qt_doc_especial",
    "qt_turmas_total", "qt_tur_infantil", "qt_tur_fundamental",
    "qt_tur_medio", "qt_tur_eja", "qt_tur_especial",
    "qt_salas_utilizadas",
]

# Colunas de tipo / categoria — preencher nulos com -1
TYPE_COLS = [
    "tp_dependencia", "tp_localizacao", "tp_situacao_funcionamento",
    "tp_categoria_escola_privada",
]


def _read_bronze_csv(filepath: str, ano: int) -> pd.DataFrame:
    """Lê um CSV do Bronze e retorna um DataFrame com as colunas mapeadas."""
    logger.info(f"Lendo arquivo: {filepath}")

    try:
        df = pd.read_csv(
            filepath,
            sep=";",
            encoding="latin-1",
            low_memory=False,
            dtype=str,        # Lê tudo como string para evitar erros de tipo
        )
    except Exception as e:
        logger.error(f"Erro ao ler {filepath}: {e}")
        return pd.DataFrame()

    logger.info(f"  Linhas lidas: {len(df):,} | Colunas: {len(df.columns)}")

    # Seleciona apenas as colunas que existem no arquivo e estão no mapa
    cols_disponiveis = {
        orig: novo
        for orig, novo in COLUMN_RENAME_MAP.items()
        if orig in df.columns
    }

    if not cols_disponiveis:
        logger.warning(f"Nenhuma coluna mapeada encontrada em {filepath}")
        return pd.DataFrame()

    df = df[list(cols_disponiveis.keys())].rename(columns=cols_disponiveis)

    # Garante que ano_censo está presente mesmo se não existia no CSV
    if "ano_censo" not in df.columns:
        df["ano_censo"] = ano

    return df


def _clean_and_type(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica tipagem, trata nulos e normaliza valores."""
    # Identificadores de texto
    for col in ["cod_escola", "nome_escola", "nome_regiao", "uf_sigla",
                "nome_uf", "nome_municipio"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace({"nan": None, "": None})

    # Inteiros de código/ano
    for col in ["ano_censo", "cod_regiao", "cod_uf", "cod_municipio"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    # Colunas de tipo/categoria
    for col in TYPE_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(-1).astype(int)

    # Indicadores 0/1
    for col in INDICATOR_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # Quantidades
    for col in QUANTITY_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    return df


def _add_missing_cols(df: pd.DataFrame) -> pd.DataFrame:
    """Adiciona com valor 0/None colunas que não existem neste ano."""
    for col in INDICATOR_COLS + QUANTITY_COLS:
        if col not in df.columns:
            df[col] = 0

    for col in TYPE_COLS:
        if col not in df.columns:
            df[col] = -1

    for col in ["nome_regiao", "uf_sigla", "nome_uf", "nome_municipio", "nome_escola"]:
        if col not in df.columns:
            df[col] = None

    for col in ["cod_regiao", "cod_uf", "cod_municipio"]:
        if col not in df.columns:
            df[col] = pd.NA

    return df


def run():
    """
    Job Bronze → Silver.
    Lê todos os anos de microdados do Bronze, normaliza e grava em Parquet particionado por ano.
    """
    bronze_path = Path(settings.BRONZE_DATA_PATH)
    silver_path = Path(settings.SILVER_DATA_PATH) / "microdados_escola"

    silver_path.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 60)
    logger.info("Iniciando pipeline Bronze → Silver")
    logger.info(f"  Bronze: {bronze_path}")
    logger.info(f"  Silver: {silver_path}")
    logger.info("=" * 60)

    # Descobre todos os anos disponíveis
    ano_dirs = sorted(bronze_path.glob("ano=*"))
    if not ano_dirs:
        logger.error(f"Nenhum diretório ano=* encontrado em {bronze_path}")
        return

    total_linhas = 0

    for ano_dir in ano_dirs:
        ano = int(ano_dir.name.split("=")[1])
        csvs = list(ano_dir.glob("microdados_ed_basica_*.csv.gz"))

        if not csvs:
            # Tenta buscar .csv normal por retrocompatibilidade local
            csvs = list(ano_dir.glob("microdados_ed_basica_*.csv"))
        
        if not csvs:
            logger.warning(f"Nenhum CSV encontrado em {ano_dir}")
            continue

        csv_path = csvs[0]
        df = _read_bronze_csv(str(csv_path), ano)

        if df.empty:
            logger.warning(f"DataFrame vazio para ano {ano}, pulando.")
            continue

        df = _add_missing_cols(df)
        df = _clean_and_type(df)

        # Garante coluna ano_censo para particionamento
        df["ano_censo"] = df["ano_censo"].fillna(ano).astype(int)

        # Ordena colunas de forma consistente
        all_cols = (
            ["ano_censo", "cod_escola", "nome_escola",
             "cod_regiao", "nome_regiao", "cod_uf", "uf_sigla", "nome_uf",
             "cod_municipio", "nome_municipio",
             "tp_dependencia", "tp_localizacao", "tp_situacao_funcionamento",
             "tp_categoria_escola_privada",
             "in_regular", "in_ead", "in_infantil", "in_fundamental",
             "in_medio", "in_profissional", "in_eja", "in_especial"]
            + QUANTITY_COLS
            + ["in_agua_potavel", "in_energia_rede_publica", "in_internet",
               "in_internet_alunos", "in_biblioteca", "in_laboratorio_info",
               "in_quadra_esportes", "in_alimentacao"]
        )
        # Reordena apenas as colunas que existem
        ordered_cols = [c for c in all_cols if c in df.columns]
        df = df[ordered_cols]

        # Salva em Parquet particionado por ano
        out_path = silver_path / f"ano={ano}"
        out_path.mkdir(parents=True, exist_ok=True)
        parquet_file = out_path / "microdados_escola.parquet"

        df.to_parquet(parquet_file, index=False, engine="pyarrow")
        total_linhas += len(df)
        logger.info(f"  ✓ Ano {ano}: {len(df):,} escolas → {parquet_file}")

    logger.info("=" * 60)
    logger.info(f"Pipeline Silver concluído. Total: {total_linhas:,} registros.")
    logger.info("=" * 60)


if __name__ == "__main__":
    run()
