import chromadb

chroma_client = chromadb.Client()

problem_collection = chroma_client.create_collection(name="problem_collection")

# Define intentions and their corresponding inputs
blockage_types = {
    "partial blockage": [
        "Partial blockage",
        "The line is partially blocked.",
        "There's something blocking part of the line.",
        "A partial blockage is interfering with the schedule!",
        "There's a minor block"
    ],
    "full blockage": [
        "Full blockage",
        "The line is fully blocked",
        "There is a major blockage",
        "The train can't get past at all.",
        "There's something blocking the whole line.",
        "There's something blocking the line"
    ]
}

# Add inputs to collection with corresponding IDs
for blockage, inputs in blockage_types.items():
    ids = [f"{blockage}_{i}" for i in range(len(inputs))]
    problem_collection.add(
        documents=inputs,
        ids=ids
    )


def get_blockage_type(user_input):
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

