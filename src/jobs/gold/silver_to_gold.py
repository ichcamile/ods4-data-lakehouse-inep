from src.config import settings
from src.utils.spark import get_spark_session
from src.utils.logger import get_logger

logger = get_logger("silver_to_gold")

def aggregate_data(df):
    """
    Applies aggregations, calculations, and KPI business logic to Silver data.
    """
    # TODO: Add aggregation logic here
    # Example:
    # return df.groupBy("ano", "regiao").agg({"indicador": "mean"})
    return df

def run():
    """
    Gold Analytical Job: Reads silver tables, computes business metrics/aggregations, writes to Gold.
    """
    logger.info("Starting Gold Aggregation (Silver -> Gold)...")
    
    spark = get_spark_session()
    
    silver_path = settings.SILVER_DATA_PATH
    gold_path = settings.GOLD_DATA_PATH
    
    logger.info(f"Reading silver data from {silver_path}")
    logger.info(f"Writing gold data to {gold_path}")
    
    # TODO: Read from Silver, aggregate and write to Gold
    # df_silver = spark.read.format("delta").load(f"{silver_path}/example_table")
    # df_gold = aggregate_data(df_silver)
    # df_gold.write.format("delta").mode("overwrite").save(f"{gold_path}/example_table")
    
    logger.info("Gold Aggregation completed successfully.")

if __name__ == "__main__":
    run()
