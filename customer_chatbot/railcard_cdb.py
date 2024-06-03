import chromadb

chroma_client = chromadb.Client()

collection = chroma_client.create_collection(name="railcard_collection")

# Define intentions and their corresponding inputs
railcards = {
    "TSU": [
        "16-17 Saver",
        "TSU",
    ],
    "YNG": [
        "16-25 Railcard",
        "YNG",
    ],
    "TST": [
        "26-30 Railcard",
        "TST",
    ],
    "NGC": [
        "annual gold card",
        "ngc",
    ],
    "DRD": [
        "dales railcard",
        "drd",
    ],
    "DCG": [
        "devon & cornwall gold card",
        "devon and cornwall gold card"
        "dcg",
    ],
    "DCR": [
        "devon & cornwall card",
        "devon and cornwall card"
        "dcr",
    ],
    "DIS": [
        "disabled persons railcard",
        "dis",
    ],
    "EVC": [
        "esk valley railcard",
        "evc",
    ],
    "FAM": [
        "family & friends railcard",
        "fam",
    ],
    "GS3": [
        "group save railcard",
        "GS3",
    ],
    "HRC": [
        "highland railcard",
        "hrc",
    ],
    "HMF": [
        "hm forces railcard",
        "hmf",
    ],
    "JCP": [
        "job centre plus travel discount card",
        "hrc",
    ],
    "CUR": [
        "my cumbria card",
        "cur",
    ],
    "none": [
        "no",
        "none",
        "don't have one",
        "I have no railcard"
    ]
}




# Add inputs to collection with corresponding IDs
for railcard, inputs in railcards.items():
    ids = [f"{railcard}_{i}" for i in range(len(inputs))]
    collection.add(
        documents=inputs,
        ids=ids
    )


def get_railcard(user_input):
    results = collection.query(
        query_texts=[user_input],
        n_results=1
    )

    # Extracting IDs from results
    ids = results["ids"][0]

    # If IDs is returned as a list, extract railcard from the first ID
    if isinstance(ids, list):
        railcard = ids[0].split("_")[0]
    else:
        railcard = ids.split("_")[0]

    return railcard

