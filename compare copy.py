import streamlit as st
import pandas as pd
from typing import List
import base64

def pairwise_comparison(df: pd.DataFrame, record_id_col: str, ignore_cols: List[str]) -> pd.DataFrame:
    df = df.sort_values(by=[record_id_col])
    results = pd.DataFrame()

    for i in range(0, len(df), 2):  # Step by 2 to process pairs
        pair = df.iloc[i:i+2]

        diffs = {record_id_col: pair[record_id_col].values[0]}  # Start with the record ID
        for col in pair.columns:
            if col not in ignore_cols:
                values = pair[col].values
                if pd.api.types.is_numeric_dtype(df[col]) and not isinstance(values[0], (bool, str)):
                    diffs[col] = abs(values[0] - values[1])
                else:
                    diffs[col] = None if values[0] == values[1] else (str(values[0]) + ' -> ' + str(values[1]))

        results = results.append(diffs, ignore_index=True)

    return results

def get_table_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  
    href = f'<a href="data:file/csv;base64,{b64}" download="differences.csv">Download Differences CSV</a>'
    return href

st.title('CSV File Pairwise Comparison Tool')
st.write("""
This app allows you to upload a CSV file and perform a pairwise comparison on the data.
The data is assumed to be arranged in pairs based on the `RECORD_ID` column. The tool 
ignores only the `RECORD_ID` column during the comparison.

After uploading your file, you can click the 'Run Analysis' button to start the comparison.
The tool will then display a list of differences between each pair of rows.

Note: This app assumes that your CSV file contains an even number of rows and that 
for every value in the `RECORD_ID` column, there are exactly two rows. 
""")

st.sidebar.header("Upload your CSV file")
uploaded_file = st.sidebar.file_uploader("Choose a file", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # Sort by `RECORD_ID` and `source` before analysis
    df = df.sort_values(by=['RECORD_ID', 'source'])
    
    st.write(df)
    
    if st.sidebar.button('Run Analysis'):
        ignore_cols = ['RECORD_ID']  # Ignore 'RECORD_ID' during the comparison
        record_id_col = 'RECORD_ID'
        df = df.astype(str)
        results = pairwise_comparison(df, record_id_col, ignore_cols)
        
        # Identify columns to drop (all N/A) except 'source'
        cols_to_drop = results.columns[results.isna().all()].tolist()
        if 'source' in cols_to_drop:
            cols_to_drop.remove('source')
        # Drop these columns
        results = results.drop(columns=cols_to_drop)

        st.write("Differences:")
        st.write(results)

        # Provide link for download
        st.sidebar.markdown(get_table_download_link(results), unsafe_allow_html=True)
