import streamlit as st

st.set_page_config(
    page_title="EMMI | Documentation"
)

st.title("Documentation")

st.write("""
   # EMMI Emissions Analysis

   ## Overview

   The **EMMI Emissions Analysis** Streamlit app provides a comprehensive platform for analyzing carbon emissions based on customer investments across various funds. It allows users to upload data files, calculate emissions, and visualize results to gain insights into their investment impacts.

   ---

   ## How to Use the App

   1. **Upload Data Files:**
      - **Portfolio File:** Contains fund names and their values.
      - **Public Equity File:** Contains public equity holdings, asset weights, and asset classes.
      - **Fixed Income File:** Contains fixed income holdings, asset weights, and asset classes.

   2. **Please upload the data files with the below structure:**
      - **Portfolio File:**
      - `FundName`: Name of the fund.
      - `FundValue`: Value of the fund.
      - **Public Equity File:**
      - `Holding Identifier`: Unique identifier for the holding.
      - `Fund`: Name of the fund.
      - `Asset Weight`: Weight of the asset in the fund.
      - `Asset Class`: Type of asset (e.g., Public Equity).
      - **Fixed Income File:**
      - `Holding Identifier`: Unique identifier for the holding.
      - `Fund`: Name of the fund.
      - `Asset Weight`: Weight of the asset in the fund.
      - `Asset Class`: Type of asset (e.g., Fixed Income).

   3. **Calculation of Emissions:**
      - **Ownership Percentage Calculation:** Calculates how much of the underlying asset the fund owns.
      - Formula: `Ownership % = (Asset Weight * FundValue) / Value`
      - **Financed Emissions Calculation:** Determines the emissions the fund is accountable for.
      - Formula: `Financed Scope n = (Ownership %) * Scope n` for `n = 1, 2, 3`
      - **Aggregation:** Summarizes emissions data:
      - By Fund Name
      - By Asset Class (Public Equity vs. Fixed Income)
      - Total Portfolio Emissions

   4. **Download Excel to Interpret Results:**
      - **Fund Aggregation:** Provides a breakdown of emissions per fund.
      - **Asset Class Aggregation:** Summarizes emissions by asset class.
      - **Total Emissions:** Gives the overall emissions impact of the entire portfolio.

   ---

   ## Technical Documentation

   1. **Data Processing:**
      - **Input Data Handling:** Reads input data files and converts them into dataframes.
      - **Validation:** Validates column names within all files and checks for required data types.
      - **Data Cleaning:** Handles NaN, missing, or invalid data, including removing or correcting problematic rows.
      - **Duplicate Handling:** Detects and resolves duplicate identifiers with different corresponding row data. Flags for manual review.
      - **Data Merging:** Merges and joins data from different sources based on identifiers and fund names.
      - **Error Reporting:** Displays errors and validation messages to help users correct data issues.
      - **Calculations:** Computes ownership percentages and financed emissions.
      - **Data Aggregation:**
      - **By Fund Name:** Aggregates financed emissions at the fund level.
      - **By Asset Class:** Groups by asset class (e.g., Fixed Income, Public Equity) and sums the financed emissions.
      - **Total Portfolio:** Computes total financed emissions across all asset classes and funds.

   2. **Visualization:**
      - **Bar Chart:** Displays financed emissions by fund and scope, showing the breakdown of emissions.
      - **Stacked Bar Chart:** Represents financed emissions categorized by scope (Scope 1, Scope 2, Scope 3) for a more detailed view.
      - **Donut Chart:** Illustrates the total portfolio emissions divided by scope (Scope 1, Scope 2, Scope 3) for a high-level overview.

   ### Technologies Used
   - **Streamlit:** For building interactive web app.
   - **Python:** Core programming language.
   - **Pandas:** For data manipulation and cleaning.
   - **Plotly:** For creating interactive charts and visualizations (used for bar charts, stacked bar charts, donut charts, and treemaps).
   - **NumPy:** For numerical operations.

""")
