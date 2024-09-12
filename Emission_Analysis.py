import streamlit as st
import pandas as pd
import plotly.express as px
from data_processing import process_files, merge_data, calculate_ownership, calculate_financed_emissions, aggregate_emissions, write_output
from validation import validate_columns

global output_file

# Page title 
st.set_page_config(
    page_title="EcoTrack | Emissions Analysis"
)

# Initialize session state for file upload tracking
if 'file_upload_status' not in st.session_state:
    st.session_state['file_upload_status'] = {'portfolio': False, 'public_equity': False, 'fixed_income': False}

# Initialize session state for submit button
if 'allow_submit' not in st.session_state:
    st.session_state['allow_submit'] = False

st.title("EcoTrack Emissions Analysis")
st.subheader("YOUR NET ZERO INVESTOR TOOLKIT")
st.sidebar.header("Upload Files")

# Define required columns for validation
required_columns = {
    'Portfolio': ['FundName', 'FundValue'],
    'PublicEquity': ['Holding Identifier', 'Fund', 'Asset Weight', 'Asset Class'],
    'FixedIncome': ['Holding Identifier', 'Fund', 'Asset Weight', 'Asset Class']
}

# Functions for uploading required 3 excel files and managing their states
def upload_portfolio_excel_file():
    global portfolio_file
    portfolio_file = st.sidebar.file_uploader("Upload Portfolio.xlsx", type=["xlsx"], key='portfolio')
    if portfolio_file:
        portfolio_df = pd.read_excel(portfolio_file)
        if validate_columns(portfolio_df, required_columns['Portfolio'], 'Portfolio.xlsx'):
            st.session_state['file_upload_status']['portfolio'] = True
            st.session_state['allow_submit'] = False
        else:
            st.session_state['file_upload_status']['portfolio'] = False
    else:
        st.session_state['allow_submit'] = False
        st.session_state['file_upload_status']['portfolio'] = False

def upload_public_equity_excel_file():
    global public_equity_file
    public_equity_file = st.sidebar.file_uploader("Upload PublicEquity.xlsx", type=["xlsx"], key='public_equity')
    if public_equity_file:
        public_equity_df = pd.read_excel(public_equity_file)
        if validate_columns(public_equity_df, required_columns['PublicEquity'], 'PublicEquity.xlsx'):
            st.session_state['file_upload_status']['public_equity'] = True
            st.session_state['allow_submit'] = False
        else:
            st.session_state['file_upload_status']['public_equity'] = False
    else:
        st.session_state['allow_submit'] = False
        st.session_state['file_upload_status']['public_equity'] = False

def upload_fixed_income_excel_file():
    global fixed_income_file
    fixed_income_file = st.sidebar.file_uploader("Upload FixedIncome.xlsx", type=["xlsx"], key='fixed_income')
    if fixed_income_file:
        fixed_income_df = pd.read_excel(fixed_income_file)
        if validate_columns(fixed_income_df, required_columns['FixedIncome'], 'FixedIncome.xlsx'):
            st.session_state['file_upload_status']['fixed_income'] = True
            st.session_state['allow_submit'] = False
        else:
            st.session_state['file_upload_status']['fixed_income'] = False
    else:
        st.session_state['allow_submit'] = False
        st.session_state['file_upload_status']['fixed_income'] = False

# Run upload functions for all three files
upload_portfolio_excel_file()
upload_public_equity_excel_file()
upload_fixed_income_excel_file()

# Submit button for final processing in the sidebar
if st.sidebar.button("Submit"):
    # Verify if file_upload_status is true for all files, if yes then updating the allow_submit state to true
    if all(st.session_state['file_upload_status'].values()):
        st.session_state['allow_submit'] = True
        st.success("""
            🎉 **Success!** 
            Your aggregated emissions data is ready for review.
        """)
    
    else:
        st.error("Please upload and validate all files before submitting.")

# Once the files are uploaded and validated and allow_submit is true, processing data and displaying main page content
if(st.session_state['allow_submit'] == True):
    # Process files by passing raw files and converting to dataframes
    portfolio_df, public_merged_df, fixed_income_merged_df = process_files(
        portfolio_file, 
        public_equity_file, 
        fixed_income_file
    )

    # Calculating ownership percentage
    public_merged_df = calculate_ownership(public_merged_df)
    fixed_income_merged_df = calculate_ownership(fixed_income_merged_df)

    # Calculating financed emissions scopes
    public_merged_df = calculate_financed_emissions(public_merged_df)
    fixed_income_merged_df = calculate_financed_emissions(fixed_income_merged_df)

    # Aggregate emissions by funds, assest class and total
    fund_aggregated, asset_class_aggregated, total_emissions = aggregate_emissions(public_merged_df, fixed_income_merged_df)

    # Save results for export file
    output_file = "Emissions_Analysis.xlsx"
    write_output(fund_aggregated, asset_class_aggregated, total_emissions, output_file)

    # Download results
    with open(output_file, 'rb') as f:
        st.download_button('📥 Download Excel File', f, file_name=output_file)
   
    # Display results
    st.subheader("Fund Aggregation")
    st.dataframe(fund_aggregated)

    st.subheader("Asset Class Aggregation")
    st.dataframe(asset_class_aggregated)

    st.subheader("Total Portfolio Emissions")
    st.dataframe(pd.DataFrame([total_emissions]))
    
    scope_labels = ['Financed Scope1', 'Financed Scope2', 'Financed Scope3']

    # Plot 1 - Financed Emissions by Scope
    st.write("### Financed Emissions by Scope")
    fig1 = px.bar(public_merged_df, x='Fund', y=scope_labels, title='Financed Emissions by Fund and Scope', barmode='group')
    # Display bar chart
    st.plotly_chart(fig1)

    # Plot 2 - Financed Emissions by Asset Class and Scope
    fig2 = px.bar(
        asset_class_aggregated,
        x='Asset Class',
        y=scope_labels,
        title='Financed Emissions by Asset Class and Scope',
        labels={'value': 'Financed Emissions', 'variable': 'Emission Scope'},  # Adjust axis labels
        barmode='stack'
    )

    # Display stacked bar chart
    st.write("### Financed Emissions by Asset Class and Scope")
    st.plotly_chart(fig2)

    # Plot 3 - Total Portfolio Emissions by Scope
    fig3 = px.pie(
        names=scope_labels, 
        values=total_emissions, 
        title="Total Portfolio Emissions by Scope",
        hole=0.4  # This makes it a donut chart
    )

    # Display donut chart
    st.write("### Total Portfolio Emissions by Scope")
    st.plotly_chart(fig3)
    
else:
    st.divider() 
    st.text("Calculate and analyze carbon emissions from your investments across funds.")
    st.text("Upload portfolio, public equity, and fixed income files to get emissions reports.")
    st.text("Explore emissions data through visualisations.")

st.sidebar.divider()
st.sidebar.markdown("Built by - [Pallavi Bhimte](https://www.linkedin.com/in/pallavi-bhimte/)")