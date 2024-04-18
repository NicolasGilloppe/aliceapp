from pymongo.mongo_client import MongoClient
import pandas as pd
import streamlit as st
from st_mongo_connection import MongoDBConnection

uri = "mongodb+srv://nicolasgilloppe:s0S8eaYt0mIMdYE7@alicedb.eqrplwk.mongodb.net/?retryWrites=true&w=majority&appName=alicedb"


connection = st.connection("mongodb", type=MongoDBConnection)
data = list(connection.find({}))
df = pd.DataFrame(data)
st.write(df)
