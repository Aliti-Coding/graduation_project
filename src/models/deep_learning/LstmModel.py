from keras import Model, layers
from typing import Optional, List



class LstmModel(Model):
    def __init__(
            self,
            vocab_size,
            embed_dim,
            lstm_layers_units: List[int] = [24, 24],
            lstm_dropout: Optional[float] = 0.5
        ) -> None:

        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.lstm_dropout = lstm_dropout
        self.lstm_layers_units = lstm_layers_units
        
        super().__init__()

        self.embedding = layers.Embedding(vocab_size, embed_dim)


        self.lstm_block = []
        for units in self.lstm_layers_units[:-1]:
            self.lstm_block.append(
                layers.LSTM(
                    units,
                    dropout = self.lstm_dropout,
                    return_sequences = True
                )
            )

        self.last_lstm = layers.LSTM(
            self.lstm_layers_units[-1],
            dropout=self.lstm_dropout,
            return_sequences = False
        )
        self.dense1 = layers.Dense(embed_dim, activation="relu")
        self.dense2 = layers.Dense(1)

    
    def call(self, x):
        x = self.embedding(x)

        for lstm_layer in self.lstm_block:
            x = lstm_layer(x)

        x = self.dense1(1)

        out = self.dense2(x) 

        return out   