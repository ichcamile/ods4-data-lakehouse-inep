from pathlib import Path
from src.config import settings
from src.utils.logger import get_logger

logger = get_logger("raw_to_bronze")


def run():
    """
    Job de validação Raw → Bronze.

    Verifica a integridade dos arquivos CSV extraídos na camada Bronze,
    reportando quais anos estão disponíveis e o número de arquivos por ano.

    Nota: A extração em si é feita pelo job `zip_to_file.py`.
    Este job serve para validar e logar o estado da camada Bronze.
    """
    bronze_path = Path(settings.BRONZE_DATA_PATH)

    logger.info("=" * 60)
    logger.info("Verificação da camada Bronze")
    logger.info(f"  Bronze: {bronze_path}")
    logger.info("=" * 60)

    ano_dirs = sorted(bronze_path.glob("ano=*"))

    if not ano_dirs:
        logger.warning("Nenhum dado encontrado na camada Bronze.")
        logger.warning("Execute primeiro: python -m src.jobs.bronze.zip_to_file")
        return

    total_arquivos = 0
    for ano_dir in ano_dirs:
        csvs = list(ano_dir.glob("*.csv"))
        total_arquivos += len(csvs)
        status = "✓" if csvs else "✗ (vazio)"
        logger.info(f"  {status} {ano_dir.name}: {len(csvs)} arquivo(s) CSV")

    logger.info("=" * 60)
    logger.info(f"Total: {len(ano_dirs)} anos | {total_arquivos} arquivo(s) CSV")
    logger.info("=" * 60)


if __name__ == "__main__":
    run()
