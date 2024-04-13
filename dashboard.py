import streamlit as st
pip install streamlit_pandas
import streamlit_pandas as sp
import pandas as pd
import mysql
from mysql import connector
from sqlalchemy import create_engine, MetaData

# Create DB Connection
db_config = {
    'user': 'root',
    'password': 'ImProTiik28',
    'host': 'localhost',
    'database': 'alice'
}
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

engine = create_engine('mysql+mysqlconnector://root:ImProTiik28@localhost/alice')
query = 'Select * From proba_1'

# Sample dataframe
df = pd.read_sql(query, engine)

# Config
st.set_page_config(page_title='Alice Predictions', page_icon=':bar_chart', layout='wide')
st.title("Today's Matchs")
st.markdown('<style>div.block-container{padding-top:1rem;}</style', unsafe_allow_html=True)

#st.write(df)
create_data = {'Pays': 'multiselect'}
all_widgets = sp.create_widgets(df[['Pays', 'Proba_H', 'Proba_D', 'Proba_A', 'Proba_HD', 'Proba_DA', 'Proba_O', 'Proba_U', 'Proba_BTTS', 'Proba_NoBTTS', 'Proba_Ho15', 'Proba_Ao15']], create_data)
df = sp.filter_df(df, all_widgets)


# Plotting
st.write(df)

