import pytest
from pyspark.sql import SparkSession

@pytest.fixture(scope="session")
def spark_session():
    """
    Fixture to construct a local SparkSession shared across all unit test cases.
    """
    spark = (
        SparkSession.builder
        .master("local[*]")
        .appName("pyspark-unit-tests")
        .config("spark.sql.shuffle.partitions", "1")
        .config("spark.default.parallelism", "1")
        .getOrCreate()
    )
    yield spark
    spark.stop()
