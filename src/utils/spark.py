from pyspark.sql import SparkSession
from src.config import settings

def get_spark_session(app_name: str = settings.APP_NAME) -> SparkSession:
    """
    Creates or retrieves an active SparkSession.
    Configures Delta Lake configuration parameters.
    """
    builder = (
        SparkSession.builder
        .appName(app_name)
        .master(settings.SPARK_MASTER)
        # Enable Delta Lake integration
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        # Optimization configuration for local/development use
        .config("spark.sql.shuffle.partitions", "2")
    )
    
    return builder.getOrCreate()
