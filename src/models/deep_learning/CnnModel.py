from keras import Sequential, layers, Model
from tensorflow import int32

class CnnModel(Model):
    def __init__(
            self,
            sequence_length,
            vocab_size,
            embed_dim,
            num_conv_blocks,
            filters,
            kernel_size,
            strides,
            head_dropout_rate

        ) -> None:

        super().__init__()

        self.sequence_length = sequence_length
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.head_dropout_rate = head_dropout_rate
        self.num_conv_blocks = num_conv_blocks
        
        self.embedding = layers.Embedding(self.sequence_length, self.embed_dim)
        
        self.reshape = layers.Reshape(
            target_shape=(self.sequence_length, self.embed_dim, 1)
        )
        
        self.conv_blocks = [
            ConvBlock(
                filters, 
                kernel_size,
                strides
            ) for _ in range(num_conv_blocks)
        ]

        self.flatten = layers.Flatten()
        self.dense1 = layers.Dense(self.sequence_length, activation="relu")
        self.dropout = layers.Dropout(self.head_dropout_rate)
        self.dense2 = layers.Dense(1)


    def call(self, x):
        embedded = self.embedding(x)
        x = self.reshape(embedded)
        
        for conv_block in self.conv_blocks:
            x = conv_block(x)

        flattened = self.flatten(x) 
        x = self.dense1(flattened) 
        out = self.dense2(x) 

        return out
    

class ConvBlock(Model):
    def __init__(
            self,
            filters,
            kernel_size,
            strides,
            **kwargs
    ) -> None:
        
        self.conv2d = layers.Conv2D(
            filters = filters, 
            kernel_size = kernel_size, 
            strides = strides,
            padding = "same"
        )
        self.pool2d = layers.MaxPooling2D(padding="same")
        self.add = layers.Add()

    def call(self, x):
        conved = self.conv2d(x)
        pooled = self.pool2d(conved)
        out = self.add([x, pooled])

        return out
