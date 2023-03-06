import keras
from transformers import TFDistilBertModel, DistilBertConfig
from keras import Model
from typing import Optional

class DistilBertModel(TFDistilBertModel):
    def __init__(
            self,
            model_name: str,
            config: Optional[DistilBertConfig] = None
        ):
        
        if config:
            model = TFDistilBertModel(config)
        else:
            model = TFDistilBertModel.from_pretrained(model_name)
        
        self.model = self._add_regression_head(
            model
        )
    

    def call(self, x):
        return self.model(x)
    
    
    @classmethod
    def _add_regression_head(
            distilbert_model: TFDistilBertModel
        ) -> keras.Model:
        
        input_ids = keras.Input(shape=(None,),dtype="int32")
        attention_mask = keras.Input(shape=(None,), dtype="int32")

        encoded = distilbert_model(
            input_ids = input_ids, 
            attention_mask = attention_mask
        )
        
        x = encoded[0][:,0,:]

        x = keras.layers.Dense(512, activation="relu")(x)
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