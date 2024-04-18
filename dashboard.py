from pymongo.mongo_client import MongoClient
import pandas as pd
import streamlit as st
from st_mongo_connection import MongoDBConnection

connection = st.connection(
    "mongodb",
    url="mongodb+srv://nicolasgilloppe:s0S8eaYt0mIMdYE7@alicedb.eqrplwk.mongodb.net/",
    database="alicedb",
    collection="Alicetest",
    kwargs={
        "retryWrites": true,
        "w": "majority",
        "maxIdleTimeMS": 180000,
        "serverSelectionTimeoutMS": 2000
    }
)
data = list(connection.find({}))
df = pd.DataFrame(data)
st.write(df)
