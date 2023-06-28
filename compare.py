import streamlit as st
import pandas as pd

# The function above goes here...
import pandas as pd
from typing import List

def pairwise_comparison(df: pd.DataFrame, record_id_col: str, ignore_cols: List[str]) -> pd.DataFrame:
    df = df.sort_values(by=[record_id_col])
    results = pd.DataFrame()

    for i in range(0, len(df), 2):  # Step by 2 to process pairs
        pair = df.iloc[i:i+2]

        # Find differences for numeric and categorical data
        diffs = {}
        for col in pair.columns:
            if col not in ignore_cols:
                values = pair[col].values
                if pd.api.types.is_numeric_dtype(df[col]) and not isinstance(values[0], (bool, str)):
                    diffs[col] = abs(values[0] - values[1])
                else:
                    diffs[col] = None if values[0] == values[1] else (str(values[0]) + ' -> ' + str(values[1]))

        results = results.append(diffs, ignore_index=True)

    return results







st.title('CSV File Pairwise Comparison Tool Version 2')
st.write("""
This app allows you to upload a CSV file and perform a pairwise comparison on the data.
The data is assumed to be arranged in pairs based on the `RECORD_ID` column. The tool 
ignores the `source` column during the comparison.

After uploading your file, you can click the 'Run Analysis' button to start the comparison.
The tool will then display a list of differences between each pair of rows.

Note: This app assumes that your CSV file contains an even number of rows and that 
for every value in the `RECORD_ID` column, there are exactly two rows. 
""")

st.sidebar.header("Upload your CSV file")
uploaded_file = st.sidebar.file_uploader("Choose a file", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write(df)
    
    if st.sidebar.button('Run Analysis'):
        ignore_cols = ['source']
        record_id_col = 'RECORD_ID'
        # convert all dataframe columns to string
        df = df.astype(str)
        results = pairwise_comparison(df, record_id_col, ignore_cols)
        
        st.write("Differences:")
        st.write(results)