import pandas as pd
import streamlit as st
import numpy as np

# Function to validate the column names in the dataframe with the required columns
def validate_columns(df, required_columns, file_name):
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(f"Missing columns in {file_name}: {', '.join(missing_columns)}")
        return False
    return True

# Remove null, NaN, invalid data types and empty values from df
def validate_data_types(df, column_types, file_type):
    invalid_rows = []

    # Remove duplicate from "Holding Identifier" entries, as this is the primary key for joining files
    if 'Holding Identifier' in df.columns:
        duplicates = df[df.duplicated('Holding Identifier', keep=False)]
        if not duplicates.empty:
            # Remove duplicates, keeping the first occurrence
            # df = df.drop_duplicates(subset='Holding Identifier', keep='first')
            # Remove duplicates, all occurrences
            df = df[df.duplicated(subset='Holding Identifier', keep=False) == False].reset_index(drop=True)
            st.warning(f"Warning: Found duplicate 'Holding Identifiers' in file: {file_type}. Refer to the table below for the holding identifiers rows that were removed from the analysis.")
            st.dataframe(duplicates)

    for column, expected_type in column_types.items():
        if expected_type == 'string':            
            # Preserve NaN values while converting other values to string
            df[column] = df[column].apply(lambda x: str(x) if pd.notna(x) else np.nan)
            
            # Check for empty or NaN values in column, as string is expected here
            empty_invalid_rows = df[df[column].isna() | (df[column].str.strip() == '')].index.tolist()
            invalid_rows.extend(empty_invalid_rows)

            # Check for numeric values in string columns (coerce numeric to NaN)
            numeric_invalid_rows = df[pd.to_numeric(df[column], errors='coerce').notna()].index.tolist()
            invalid_rows.extend(numeric_invalid_rows)
    
        elif expected_type == 'float':
            # Collect rows where the conversion resulted in NaN (indicating invalid float)
            invalid_rows.extend(df[df[column].isna()].index.tolist())
            # Coerce errors to NaN for invalid float values
            df[column] = pd.to_numeric(df[column], errors='coerce')

    # Drop invalid rows and store them in session state
    invalid_rows = list(set(invalid_rows))  # Remove duplicates from the list
    invalid_df = df.loc[invalid_rows].copy() 
    df = df.drop(invalid_rows).reset_index(drop=True)

    if invalid_rows:
        st.warning(f"Warning: Invalid data detected in file: {file_type}. Refer to the table below for the rows that were removed from the analysis.")
        st.dataframe(invalid_df)

    return df
