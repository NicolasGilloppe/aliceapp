from pymongo.mongo_client import MongoClient
import pandas as pd
import streamlit as st
from st_mongo_connection import MongoDBConnection


connection = st.connection("mongodb", type=MongoDBConnection)
db = connection["alicedb"]
collection = db["users"]


data = list(collection.find({}))
df = pd.DataFrame(data)
st.write(df)
