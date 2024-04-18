from pymongo.mongo_client import MongoClient
import pandas as pd
import streamlit as st
from st_mongo_connection import MongoDBConnection


connection = st.connection("mongodb", type=MongoDBConnection)
data = list(connection.find({}))
df = pd.DataFrame(data)
st.write(df)

conn = st.connection("mongodb2", type=MongoDBConnection)
data2 = list(conn.find({}))
df2 = pd.DataFrame(data2)
st.write(df2)
