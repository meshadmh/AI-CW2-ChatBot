import spacy.cli
import warnings

# Filter out specific warning
warnings.filterwarnings("ignore")

nlp = spacy.load('en_core_web_lg')

# Load station names from stations.txt
stratford = []
shenfield = []
chelmsford = []
colchester = []
manningtree = []
derby = []
stowmarket = []
diss = []
norwich = []

with open("data/stations.txt") as f:
    for line in f:
        parts = line.strip().split(' | ')
        station_name = parts[0].strip().upper()  # Convert station name to full capitals
        if "STRATFORD" in station_name:
            stratford.append(parts[1].strip())
        elif "SHENFIELD" in station_name:
            shenfield.append(parts[1].strip())
        elif "CHELMSFORD" in station_name:
            chelmsford.append(parts[1].strip())
        elif "COLCHESTER" in station_name:
            colchester.append(parts[1].strip())
        elif "MANNINGTREE" in station_name:
            manningtree.append(parts[1].strip())
        elif "DERBY" in station_name:
            derby.append(parts[1].strip())
        elif "STOWMARKET" in station_name:
            stowmarket.append(parts[1].strip())
        elif "DISS" in station_name:
            diss.append(parts[1].strip())
        elif "NORWICH" in station_name:
            norwich.append(parts[1].strip())


# Match loaded sentences with appropriate labels for use with spacy
labels = []
sentences = []

for sentence_list, label in [(stratford, 'STRATFORD'),
                              (shenfield, 'SHENFIELD'),
                              (chelmsford, 'CHELMSFORD'),
                              (colchester, 'COLCHESTER'),
                              (manningtree, 'MANNINGTREE'),
                              (derby, 'DERBY ROAD'),
                              (stowmarket, 'STOWMARKET'),
                              (diss, 'DISS'),
                              (norwich, 'NORWICH')]:
    for sentence in sentence_list:
        labels.append(label)
        sentences.append(sentence.lower().strip())


def check_station_name(station_input):
    doc_1 = nlp(station_input)
    similarities = {}

    # compare user input to each intentions sentence and generate a similarity score
    for index, sentence in enumerate(sentences):
        doc_2 = nlp(sentence)
        similarity = doc_2.similarity(doc_1)
        similarities[index] = similarity

    max_similarity_idx = max(similarities, key=similarities.get)
    # minimum acceptable similarity to accept an intention
    min_similarity = 0.6

    if similarities[max_similarity_idx] > min_similarity:
        return labels[max_similarity_idx]
    else:
        return 'unclear'
