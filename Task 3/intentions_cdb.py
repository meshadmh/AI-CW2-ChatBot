# -*- coding: utf-8 -*-
"""
Created on Fri May 31 10:37:43 2024

@author: dan
"""
import chromadb

chroma_client = chromadb.Client()

problem_collection = chroma_client.get_or_create_collection(name="intention_collection")

# Define intentions and their corresponding inputs
blockage_types = {
    "yes": [
        "yes",
        "yeah",
        "sure",
        "ok",
        "certainly"
    ],
    "no": [
        "no",
        "nope",
        "negative",
        "no thanks"

    ],
    "greeting": [
        "hello",
        "hi",
        "hey",
        "heya",
        "yo"
    ],
}

# Add inputs to collection with corresponding IDs
for blockage, inputs in blockage_types.items():
    ids = [f"{blockage}_{i}" for i in range(len(inputs))]
    problem_collection.add(
        documents=inputs,
        ids=ids
    )


def get_intentions(user_input):
    results = problem_collection.query(
        query_texts=[user_input],
        n_results=1
    )

    # Extracting IDs from results
    ids = results["ids"][0]

    # If IDs is returned as a list, extract intention from the first ID
    if isinstance(ids, list):
        blockage_type = ids[0].split("_")[0]
    else:
        blockage_type = ids.split("_")[0]

    return blockage_type