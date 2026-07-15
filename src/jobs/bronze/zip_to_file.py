import zipfile
import os
import shutil
from pathlib import Path
from src.config import settings
from src.utils.logger import get_logger

logger = get_logger("zip_to_file")


def run(anos: range = range(2007, 2025)):
    """
    Extrai os arquivos CSV dos zips do Censo Escolar para a camada Bronze.

    Espera encontrar em data/raw/ arquivos nomeados como:
      - microdados_censo_escolar_{ano}.zip
      - microdados_censo_escolar_{ano}_.zip   (variante com underscore)

    Para cada ano, extrai apenas os CSVs dentro do subdiretório 'dados/'
    e os salva em data/bronze/ano={ano}/.

    Args:
        anos: Range de anos a processar. Padrão: 2007–2024.
    """
    raw_path = Path(settings.RAW_DATA_PATH)
    bronze_path = Path(settings.BRONZE_DATA_PATH)

    logger.info("=" * 60)
    logger.info("Iniciando extração ZIP → Bronze")
    logger.info(f"  Raw:    {raw_path}")
    logger.info(f"  Bronze: {bronze_path}")
    logger.info("=" * 60)

    for ano in anos:
        # Aceita nome com ou sem underscore trailing
        candidatos = [
            raw_path / f"microdados_censo_escolar_{ano}_.zip",
            raw_path / f"microdados_censo_escolar_{ano}.zip",
        ]

        zip_path = next((p for p in candidatos if p.exists()), None)

        if zip_path is None:
            logger.warning(f"ZIP não encontrado para ano {ano}, pulando.")
            continue

        destino = bronze_path / f"ano={ano}"
        destino.mkdir(parents=True, exist_ok=True)

        logger.info(f"Extraindo {zip_path.name} → {destino}")

        with zipfile.ZipFile(zip_path, "r") as zf:
            for entry in zf.namelist():
                # Extrai apenas CSVs dentro do diretório 'dados/'
                if "dados/" in entry.lower() and entry.lower().endswith(".csv"):
                    nome_arquivo = os.path.basename(entry)
                    if not nome_arquivo:
                        continue

                    destino_arquivo = destino / nome_arquivo
                    with zf.open(entry) as src, open(destino_arquivo, "wb") as dst:
                        shutil.copyfileobj(src, dst)

                    logger.info(f"  → Salvo: {destino_arquivo.name}")

    logger.info("=" * 60)
    logger.info("Extração concluída.")
    logger.info("=" * 60)


if __name__ == "__main__":
    run()
