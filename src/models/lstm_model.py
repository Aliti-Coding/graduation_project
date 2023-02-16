import keras
import os
from keras import layers
from keras.layers import TextVectorization
import tensorflow as tf

VOCAB_SIZE = 15000
SEQUENCE_LENGTH = 100
EMBED_DIM = 24

def load_model_weights_from_checkpoint(model:keras.Model=None) -> keras.Model:
    """
    Example:
        >>> model = load_model_weights_from_checkpoint()
        >>> model.predict(["bad"])
    """

    # Create model if model not explicitly provided
    if not model:
        model = create_lstm_model()
    
    model.load_weights(r"checkpoints/lstm_model_24_24_250k_rows/model")

    return model

def create_lstm_model() -> keras.Model:
    
    vectorize_layer = load_vectorization_layer()

    lstm_model = keras.Sequential(
        [
            layers.Input(shape=(1,), dtype="string"),
            vectorize_layer,
            layers.Embedding(VOCAB_SIZE, EMBED_DIM),
            layers.LSTM(24, dropout=0.5, return_sequences=True),
            layers.LSTM(24, dropout=0.5),
            layers.Dense(1)
        ]
    )

    return lstm_model

def load_vectorization_layer() -> TextVectorization:

    target = "vectorization_vocabulary.txt"

    if target not in os.listdir("checkpoints"):
        raise Exception(f"could not find '{target}', did you place it in the correct folder and or forget to download it?")
        
    with open("checkpoints/vectorization_vocabulary.txt", "r") as file:
        vocab = file.read()
        vocab=vocab.split("\n")[:-1] #last line is an empty string

    return create_vectorization_layer(vocab)
    

def create_vectorization_layer(vocab=None):
    vectorize_layer = layers.TextVectorization(
        VOCAB_SIZE,
        "lower_and_strip_punctuation",
        output_mode="int",
        output_sequence_length=SEQUENCE_LENGTH,
        vocabulary=vocab
    )

    return vectorize_layer