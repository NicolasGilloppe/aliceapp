import mysql.connector
import streamlit as st
import streamlit_pandas as sp
import pandas as pd
import mysql
from mysql import connector
from sqlalchemy import create_engine, MetaData

# Config
st.set_page_config(page_title='Alice Predictions', page_icon=':bar_chart', layout='wide')
st.title("Today's Matchs")
st.markdown('<style>div.block-container{padding-top:1rem;}</style', unsafe_allow_html=True)


# Create DB Connection
db_config = {
    'user': 'root',
    'password': 'ImProTiik28',
    'host': 'localhost',
    'database': 'alice'
}

my_db = mysql.connector.connect(user = 'root', password = 'ImProTiik28', host = 'localhost', database = 'alice')
mycursor = my_db.cursor()
mycursor.execute("Select * From proba_1")
result = mycursor.fetchall()
df = pd.DataFrame(result)
df.columns = ['Date', 'Time', 'Champ', 'Home', 'Away', 'Pays', 'Proba_H', 'Proba_D', 'Proba_A', 'Proba_HD', 'Proba_DA', 'Proba_O', 'Proba_U', 'Proba_BTTS', 'Proba_NoBTTS', 'Proba_Ho15', 'Proba_Ao15']

#st.write(df)
create_data = {'Pays': 'multiselect'}
all_widgets = sp.create_widgets(df[['Pays', 'Proba_H', 'Proba_D', 'Proba_A', 'Proba_HD', 'Proba_DA', 'Proba_O', 'Proba_U', 'Proba_BTTS', 'Proba_NoBTTS', 'Proba_Ho15', 'Proba_Ao15']], create_data)
df = sp.filter_df(df, all_widgets)


# Plotting
st.write(df)




