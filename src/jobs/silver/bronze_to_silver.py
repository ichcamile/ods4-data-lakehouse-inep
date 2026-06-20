from src.config import settings
from src.utils.spark import get_spark_session
from src.utils.logger import get_logger

logger = get_logger("bronze_to_silver")

def clean_data(df):
    """
    Cleans Bronze data by renaming columns, casting types, handling nulls.
    """
    # TODO: Add transformation/cleaning logic here
    return df

def run():
    """
    Silver Transformation Job: Reads bronze tables, cleans/normalizes data, writes to Silver.
    """
    logger.info("Starting Silver Transformation (Bronze -> Silver)...")
    
    spark = get_spark_session()
    
    bronze_path = settings.BRONZE_DATA_PATH
    silver_path = settings.SILVER_DATA_PATH
    
    logger.info(f"Reading bronze data from {bronze_path}")
    logger.info(f"Writing silver data to {silver_path}")
    
    # TODO: Read from Bronze, clean/transform and write to Silver
    # df_bronze = spark.read.format("delta").load(f"{bronze_path}/example_table")
    # df_silver = clean_data(df_bronze)
    # df_silver.write.format("delta").mode("overwrite").save(f"{silver_path}/example_table")
    
    logger.info("Silver Transformation completed successfully.")

if __name__ == "__main__":
    run()
