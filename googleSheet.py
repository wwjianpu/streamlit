import streamlit as st
import pandas as pd
from gsheetsdb import connect

# Create a connection object
conn = connect()


# Perform SQL query on the Google Sheet.
# Uses st.cache to only rerun when the query changes or after 10 min.
@st.cache(ttl=60)
def run_query(query):
    rows = conn.execute(query, headers=1)
    return rows

sheet_url = st.secrets["url"]["public_gsheets_url_bed_loc_map"]
rows = run_query(f'SELECT * FROM "{sheet_url}"')


# Print results.
for row in rows:
    #st.write(f"{row.hospCode} has a :{row.pet}:")
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("hospCode", row.hospCode)
        col2.metric("fromBed", int(row.fromBed))
        col3.metric("toBed", int(row.toBed))
        col4.metric("Location", f'{row.Location}')

#df = pd.DataFrame(rows, columns=["hospCode", "fromBed", "toBed", "Location"])
df = pd.DataFrame(rows)
st.write(df)


