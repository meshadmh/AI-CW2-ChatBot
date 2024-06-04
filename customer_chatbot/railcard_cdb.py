import chromadb

chroma_client = chromadb.Client()

collection = chroma_client.create_collection(name="railcard_collection")

# Define intentions and their corresponding inputs
railcards = {
    "16-17 Saver": [
        "16-17 Saver",
        "TSU railcard",
    ],
    "16-25 Railcard": [
        "16-25 Railcard",
        "YNG railcard",
    ],
    "26-30 Railcard": [
        "26-30 Railcard",
        "TST railcard",
    ],
    "Annual Gold Card": [
        "annual gold card",
        "ngc railcard",
    ],
    "Dales Railcard": [
        "dales railcard",
        "drd railcard",
    ],
    "Devon & Cornwall Gold Card": [
        "devon & cornwall gold card",
        "devon and cornwall gold card"
        "dcg railcard",
    ],
    "Devon & Cornwall Card": [
        "devon & cornwall card",
        "devon and cornwall card"
        "dcr railcard",
    ],
    "Disabled Persons Railcard": [
        "disabled persons railcard",
        "dis railcard",
    ],
    "Esk Valley Railcard": [
        "esk valley railcard",
        "evc railcard",
    ],
    "Family & Friends Railcard": [
        "family & friends railcard",
        "fam railcard",
    ],
    "Group Save Railcard": [
        "group save railcard",
        "GS3 railcard",
    ],
    "Highland Railcard": [
        "highland railcard",
        "hrc railcard",
    ],
    "HM Forces Railcard": [
        "hm forces railcard",
        "hmf railcard",
    ],
    "Jobcentre Plus Travel Discount Card": [
        "job centre plus travel discount card",
        "hrc railcard",
    ],
    "MyCumbria Card": [
        "my cumbria card",
        "cur railcard",
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

