from pymongo.mongo_client import MongoClient
import pandas as pd
import streamlit as st

uri = "mongodb+srv://nicolasgilloppe:s0S8eaYt0mIMdYE7@alicedb.eqrplwk.mongodb.net/?retryWrites=true&w=majority&appName=alicedb"

# Create a new client and connect to the server
cluster = MongoClient(uri, connectTimeoutMS=30000, socketTimeoutMS=30000)
db= cluster["alicedb"]
collection = db['Alicetest']

#Get Datas from Mongo to Df
data = list(collection.find({}))

df = pd.DataFrame(data)

st.write(df)
