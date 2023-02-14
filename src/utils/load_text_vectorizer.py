from keras import layers

VOCAB_SIZE = 15000
SEQUENCE_LENGTH = 100

def load_vectorizer():
    with open("../../checkpoints/vectorization_vocabulary.txt", "r") as file:
        vocab = file.read()
        vocab=vocab.split("\n")[:-1] #last line is an empty string

    vectorize_layer = layers.TextVectorization(
        VOCAB_SIZE,
        "strip_punctuation",
        output_mode="int",
        output_sequence_length=SEQUENCE_LENGTH,
        vocabulary=vocab
    )

    return vectorize_layer