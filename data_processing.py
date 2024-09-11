import pandas as pd
from validation import validate_data_types
import streamlit as st

def process_files(portfolio_file, public_equity_file, fixed_income_file):
    # Read files
    portfolio_df, public_equity_df, fixed_income_df = read_files(
        portfolio_file, 
        public_equity_file, 
        fixed_income_file
    )
    
    # Handle if df has no rows
    if portfolio_df is None or public_equity_df is None or fixed_income_df is None:
        st.error(f"Error: One or more DataFrames are None after reading and validation.")
        return None, None, None  

    public_universe_df = pd.read_csv('data/public_universe.csv')
    fixed_income_universe_df = pd.read_csv('data/fixed_income_universe.csv')

    # Merge the data
    public_merged_df, fixed_income_merged_df = merge_data(public_equity_df, public_universe_df, fixed_income_df, fixed_income_universe_df, portfolio_df)

    # Handle if df has no rows
    if public_merged_df is None or fixed_income_merged_df is None:
        st.error(f"Error: One or more merged DataFrames are None after merging.")
        return None, None, None  

    return portfolio_df, public_merged_df, fixed_income_merged_df

def read_files(portfolio_file, public_equity_file, fixed_income_file):
    try:
        portfolio_df = pd.read_excel(portfolio_file)
        public_equity_df = pd.read_excel(public_equity_file)
        fixed_income_df = pd.read_excel(fixed_income_file)
    except Exception as e:
        st.error(f"Error reading files")
        return None, None, None

    # Define column types based on file type
    column_types = {
        'Portfolio': {'FundName': 'string', 'FundValue': 'float'},
        'PublicEquity': {'Holding Identifier': 'string', 'Fund': 'string', 'Asset Weight': 'float', 'Asset Class': 'string'},
        'FixedIncome': {'Holding Identifier': 'string', 'Fund': 'string', 'Asset Weight': 'float', 'Asset Class': 'string'},
    }

    try:
        # Validate data types
        portfolio_df = validate_data_types(portfolio_df, column_types['Portfolio'], "portfolio")
        public_equity_df = validate_data_types(public_equity_df, column_types['PublicEquity'], "public_equity")
        fixed_income_df = validate_data_types(fixed_income_df, column_types['FixedIncome'], "fixed_income")
        
    except Exception as e:
        st.error(f"Error in validation or missing data handling")
        return None, None, None

    return portfolio_df, public_equity_df, fixed_income_df

def merge_data(public_equity_df, public_universe_df, fixed_income_df, fixed_income_universe_df, portfolio_df):
    try:
        # Merging PublicEquityHoldings with public_universe.csv
        public_merged_df = pd.merge(public_equity_df, public_universe_df, left_on='Holding Identifier', right_on='Identifier', how='left')

        # Merging FixedIncomeHoldings with fixed_income_universe.csv
        fixed_income_merged_df = pd.merge(fixed_income_df, fixed_income_universe_df, left_on='Holding Identifier', right_on='Identifier', how='left') 

        # Merge both datasets with the portfolio to get FundValue
        public_merged_df = pd.merge(public_merged_df, portfolio_df, left_on='Fund', right_on='FundName', how='left')
        fixed_income_merged_df = pd.merge(fixed_income_merged_df, portfolio_df, left_on='Fund', right_on='FundName', how='left')
    except Exception as e:
        st.error(f"Error during merging")
        return None, None

    return public_merged_df, fixed_income_merged_df
    

def calculate_ownership(merged_df):
    # Calculate ownership per asset
    merged_df['Ownership %'] = (merged_df['Asset Weight'] * merged_df['FundValue']) / merged_df['Value']
    return merged_df

def calculate_financed_emissions(merged_df):
    # Calculate financed emissions for each asset
    for scope in ['Scope1', 'Scope2', 'Scope3']:
        merged_df[f'Financed {scope}'] = merged_df['Ownership %'] * merged_df[scope]
    return merged_df

def aggregate_emissions(public_merged_df, fixed_income_merged_df):
    # Group-by on the Fund Name and sum up all the financed emissions
    fund_aggregated = pd.concat([public_merged_df, fixed_income_merged_df]).groupby('Fund').agg({
        'Financed Scope1': 'sum',
        'Financed Scope2': 'sum',
        'Financed Scope3': 'sum'
    }).reset_index()

    # Group-by on the Asset Class (Fixed Income vs Public Equity) and sum all the financed emissions
    asset_class_aggregated = pd.concat([public_merged_df, fixed_income_merged_df]).groupby('Asset Class').agg({
        'Financed Scope1': 'sum',
        'Financed Scope2': 'sum',
        'Financed Scope3': 'sum'
    }).reset_index()

    # Sum up all the financed emissions for a total portfolio number
    total_emissions = {
        'Total Scope1': asset_class_aggregated['Financed Scope1'].sum(),
        'Total Scope2': asset_class_aggregated['Financed Scope2'].sum(),
        'Total Scope3': asset_class_aggregated['Financed Scope3'].sum()
    }

    return fund_aggregated, asset_class_aggregated, total_emissions

def write_output(fund_aggregated, asset_class_aggregated, total_emissions, output_file):
    # Write output to Excel file
    with pd.ExcelWriter(output_file) as writer:
        fund_aggregated.to_excel(writer, sheet_name='Fund Aggregation', index=False)
        asset_class_aggregated.to_excel(writer, sheet_name='Asset Class Aggregation', index=False)
        pd.DataFrame([total_emissions]).to_excel(writer, sheet_name='Total Emissions', index=False)
