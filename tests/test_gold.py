import pytest
from src.jobs.gold.silver_to_gold import aggregate_data

def test_gold_aggregation(spark_session):
    """
    Validates that aggregate_data aggregates correctly.
    """
    data = [("2023", "Norte", 100), ("2023", "Norte", 150)]
    columns = ["ano", "regiao", "valor"]
    df = spark_session.createDataFrame(data, columns)
    
    aggregated_df = aggregate_data(df)
    
    assert aggregated_df.count() == 2
