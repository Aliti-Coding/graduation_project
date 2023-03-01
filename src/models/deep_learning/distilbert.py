import keras
from transformers import TFDistilBertModel


def add_regression_head(distilbert_model:TFDistilBertModel) -> keras.Model:
    
    input_ids = keras.Input(shape=(None,),dtype="int32")
    attention_mask = keras.Input(shape=(None,), dtype="int32")

    encoded = distilbert_model(input_ids=input_ids, attention_mask=attention_mask)
    x = encoded[:,0,:]

    x = keras.layers.Dense(768, activation="relu")(x)
    x = keras.layers.Dense(32, activation="relu")(x)
    outputs = keras.layers.Dense(1)(x)

    distilbert_w_regressor_head = keras.Model(
        inputs={
            "input_ids":input_ids, 
            "attention_mask":attention_mask
        }, 
        outputs=outputs
    )

    return distilbert_w_regressor_head