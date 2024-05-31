# -*- coding: utf-8 -*-
"""
Created on Fri May 31 08:37:10 2024

@author: dan
"""
import chromadb

chroma_client = chromadb.Client()

staff_collection = chroma_client.get_or_create_collection(name="staff_collection")

# Define intentions and their corresponding inputs
staff_types = {
    # "manager": [
    #     "manager"
    # ],
    "signaller": [
        "signaller",
    ],
    "rail staff": [
        "rail staff",
        "station staff",
        "train staff"
    ],
    "passenger": [
        "passenger",
        "stranded passenger"
    ]
}

# Add inputs to collection with corresponding IDs
for staff, inputs in staff_types.items():
    ids = [f"{staff}_{i}" for i in range(len(inputs))]
    staff_collection.add(
        documents=inputs,
        ids=ids
    )

def get_staff_type(user_input):
    results = staff_collection.query(
        query_texts=[user_input],
        n_results=1
    )

    # Extracting IDs from results
    ids = results["ids"][0]
    confidence_scores = results.get("confidence_scores")

    # If IDs is returned as a list, extract intention from the first ID
    if isinstance(ids, list):
        staff_type = ids[0].split("_")[0]
        confidence = confidence_scores[0] if confidence_scores else None
    else:
        staff_type = ids.split("_")[0]
        confidence = confidence_scores if confidence_scores else None

    return staff_type#, confidence
