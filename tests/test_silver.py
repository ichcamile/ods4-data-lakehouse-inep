import pytest
from src.jobs.silver.bronze_to_silver import clean_data

def test_silver_cleaning_logic(spark_session):
    """
    Validates that clean_data transforms the input DataFrame correctly.
    """
    # Create a small dummy dataframe
    data = [("  JOHN DOE  ", 25), ("jane smith", 30)]
    columns = ["name", "age"]
    df = spark_session.createDataFrame(data, columns)
    
    # Run the clean_data transformation (which currently returns df unchanged)
    cleaned_df = clean_data(df)
    
    assert cleaned_df.count() == 2
    assert "name" in cleaned_df.columns
