import pytest
from src.jobs.bronze import raw_to_bronze

def test_bronze_ingestion_placeholder(spark_session):
    """
    Placeholder test for bronze layer ETL pipeline.
    """
    # Verify that spark_session is correctly injected
    assert spark_session is not None
    assert spark_session.version is not None
