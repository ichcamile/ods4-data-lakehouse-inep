"""
Job de ingestão: Download direto dos ZIPs do INEP → extração para camada Bronze.

Baixa os microdados do Censo Escolar diretamente de download.inep.gov.br
sem necessidade de arquivos locais, e extrai os CSVs para a camada Bronze.

Compatível com:
- Execução local (Python padrão)
- Databricks (usando /dbfs/ ou volumes Unity Catalog como caminho de saída)
"""
import io
import os
import sys
import shutil
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# ---------------------------------------------------------------------------
# Bootstrap do sys.path — garante que 'src.*' funciona em qualquer ambiente:
# execução local, `python -m`, Databricks Jobs e Databricks Notebooks.
# ---------------------------------------------------------------------------
_THIS_FILE = Path(__file__).resolve()
# Sobe 3 níveis: ingest_from_web.py -> bronze -> jobs -> src -> ROOT
_PROJECT_ROOT = _THIS_FILE.parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
# ---------------------------------------------------------------------------

from src.config import settings
from src.utils.logger import get_logger

logger = get_logger("ingest_from_web")

# ---------------------------------------------------------------------------
# Mapa de URLs — download.inep.gov.br
# Padrão confirmado no portal oficial:
#   2004–2024 : .../microdados_censo_escolar_{ano}.zip
#   2025+     : .../microdados_censo_escolar_{ano}_.zip  (underscore trailing)
# Anos sem publicação: 2020 (INEP não divulgou dados de 2020)
# ---------------------------------------------------------------------------
BASE_URL = "https://download.inep.gov.br/dados_abertos"

# Anos com URL no formato especial (underscore trailing)
ANOS_COM_UNDERSCORE = {2025}

# Anos que o INEP não publicou microdados (pular sem erro)
ANOS_SEM_DADOS = {2020}


def _build_url(ano: int) -> str:
    """Retorna a URL de download do ZIP para um dado ano."""
    sufixo = "_" if ano in ANOS_COM_UNDERSCORE else ""
    return f"{BASE_URL}/microdados_censo_escolar_{ano}{sufixo}.zip"


def _download_e_extrair(ano: int, bronze_path: Path, chunk_size: int = 8 * 1024 * 1024) -> bool:
    """
    Baixa o ZIP do INEP em memória (streaming) e extrai apenas os CSVs
    do subdiretório 'dados/' para bronze_path/ano={ano}/.

    Args:
        ano:         Ano do Censo a processar.
        bronze_path: Diretório raiz da camada Bronze.
        chunk_size:  Tamanho do chunk de leitura em bytes (padrão: 8 MB).

    Returns:
        True se ao menos 1 CSV foi extraído, False caso contrário.
    """
    if ano in ANOS_SEM_DADOS:
        logger.warning(f"Ano {ano} sem dados publicados pelo INEP — pulando.")
        return False

    url = _build_url(ano)
    destino = bronze_path / f"ano={ano}"
    destino.mkdir(parents=True, exist_ok=True)

    logger.info(f"[{ano}] Baixando: {url}")

    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; ODS4-Lakehouse)"})
        with urlopen(req, timeout=300) as response:
            # Lê o ZIP inteiro em memória (streaming por chunks para evitar OOM)
            buffer = io.BytesIO()
            total_bytes = 0
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                buffer.write(chunk)
                total_bytes += len(chunk)
                mb = total_bytes / 1_048_576
                if int(mb) % 100 == 0 and mb > 0:
                    logger.info(f"  [{ano}] Baixado: {mb:.0f} MB...")

            buffer.seek(0)
            logger.info(f"  [{ano}] Download concluído: {total_bytes / 1_048_576:.1f} MB")

    except HTTPError as e:
        logger.error(f"  [{ano}] HTTP {e.code} ao acessar {url}: {e.reason}")
        return False
    except URLError as e:
        logger.error(f"  [{ano}] Erro de rede ao acessar {url}: {e.reason}")
        return False

    # Extrai CSV(s) do subdiretório 'dados/'
    csvs_extraidos = 0
    try:
        with zipfile.ZipFile(buffer, "r") as zf:
            for entry in zf.namelist():
                if "dados/" in entry.lower() and entry.lower().endswith(".csv"):
                    nome_arquivo = os.path.basename(entry)
                    if not nome_arquivo:
                        continue
                    destino_arquivo = destino / nome_arquivo
                    with zf.open(entry) as src, open(destino_arquivo, "wb") as dst:
                        shutil.copyfileobj(src, dst)
                    csvs_extraidos += 1
                    logger.info(f"  [{ano}] Extraído: {nome_arquivo}")
    except zipfile.BadZipFile:
        logger.error(f"  [{ano}] Arquivo ZIP inválido ou corrompido.")
        return False

    if csvs_extraidos == 0:
        logger.warning(f"  [{ano}] Nenhum CSV encontrado no ZIP (verifique a estrutura interna).")
        return False

    logger.info(f"  [{ano}] ✓ {csvs_extraidos} arquivo(s) extraído(s) → {destino}")
    return True


def run(ano_inicio: int = 2004, ano_fim: int = 2024, forcar_redownload: bool = False):
    """
    Baixa e extrai os microdados do Censo Escolar diretamente do INEP.

    Para cada ano no intervalo [ano_inicio, ano_fim], verifica se o CSV
    já existe na camada Bronze. Se já existir, pula (a menos que
    forcar_redownload=True).

    Args:
        ano_inicio:         Primeiro ano a processar (inclusive). Padrão: 2004.
        ano_fim:            Último ano a processar (inclusive). Padrão: 2024.
        forcar_redownload:  Se True, baixa mesmo que o CSV já exista. Padrão: False.
    """
    bronze_path = Path(settings.BRONZE_DATA_PATH)
    bronze_path.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 60)
    logger.info("Iniciando ingestão web: INEP → Bronze")
    logger.info(f"  Anos: {ano_inicio}–{ano_fim}")
    logger.info(f"  Bronze: {bronze_path}")
    logger.info(f"  Forçar re-download: {forcar_redownload}")
    logger.info("=" * 60)

    sucessos, pulados, erros = 0, 0, 0

    for ano in range(ano_inicio, ano_fim + 1):
        if ano in ANOS_SEM_DADOS:
            logger.info(f"[{ano}] Sem publicação pelo INEP — pulando.")
            pulados += 1
            continue

        destino_ano = bronze_path / f"ano={ano}"
        csvs_existentes = list(destino_ano.glob("*.csv")) if destino_ano.exists() else []

        if csvs_existentes and not forcar_redownload:
            logger.info(f"[{ano}] Já processado ({len(csvs_existentes)} CSV(s)) — pulando.")
            pulados += 1
            continue

        ok = _download_e_extrair(ano, bronze_path)
        if ok:
            sucessos += 1
        else:
            erros += 1

    logger.info("=" * 60)
    logger.info("Ingestão concluída.")
    logger.info(f"  ✓ Baixados com sucesso: {sucessos}")
    logger.info(f"  ⏭  Pulados:             {pulados}")
    logger.info(f"  ✗ Erros:               {erros}")
    logger.info("=" * 60)


if __name__ == "__main__":
    run()
