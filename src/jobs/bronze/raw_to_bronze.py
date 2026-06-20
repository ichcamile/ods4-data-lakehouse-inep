from src.config import settings
from src.utils.spark import get_spark_session
from src.utils.logger import get_logger

logger = get_logger("raw_to_bronze")

def run():
    """
    Bronze Ingestion Job: Reads raw data and writes to Delta/Parquet Bronze tables.
    """
    logger.info("Starting Bronze Ingestion (Raw -> Bronze)...")
    
    spark = get_spark_session()
    
    # Example raw ingestion setup (change file type / options as needed)
    raw_path = settings.RAW_DATA_PATH
    bronze_path = settings.BRONZE_DATA_PATH
    
    logger.info(f"Reading raw data from {raw_path}")
    logger.info(f"Writing bronze data to {bronze_path}")
    
    # TODO: Add specific ingestion logic for INEP microdata (e.g. ENEM, Censo)
    # df = spark.read.format("csv").option("header", "true").option("delimiter", ";").load(f"{raw_path}/example_raw.csv")
    # df.write.format("delta").mode("overwrite").save(f"{bronze_path}/example_table")
    
    logger.info("Bronze Ingestion completed successfully.")

if __name__ == "__main__":
    run()
