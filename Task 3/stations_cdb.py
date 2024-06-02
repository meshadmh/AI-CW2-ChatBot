# -*- coding: utf-8 -*-
"""
Created on Fri May 31 09:16:57 2024

@author: dan
"""
import chromadb
import pandas as pd
import warnings

# Filter out specific warning
warnings.filterwarnings("ignore")
df = pd.read_csv('station_names.csv')
df = pd.DataFrame(df)

chroma_client = chromadb.PersistentClient(path="/station_name_folder")

collection = chroma_client.get_or_create_collection(name="station_name_collection")

documents = df["spelling"].tolist()
print(documents)
#%%
collection.add(
    documents=documents,
    ids=[f"{i}" for i in range(len(documents))]
)


#%%
def get_best_station(user_input):
    
    results = collection.query(
        query_texts=[user_input], # Chroma will embed this for you
        n_results=3 # how many results to return
    )
    closest_match = int(results["ids"][0][0])
    
    return df["name"][closest_match]

print(get_best_station("colchester"))
print(get_best_station("ipswitch"))
print(get_best_station("colchst"))
print(get_best_station("shnfield"))
print(get_best_station("shenfield"))
print(get_best_station("diss"))
print(get_best_station("haughely"))
print(get_best_station("clemsford"))
print(get_best_station("Clemsford "))