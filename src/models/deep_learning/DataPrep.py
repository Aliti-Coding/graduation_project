
from transformers import PreTrainedTokenizer
from sklearn.model_selection import train_test_split
from keras.layers import TextVectorization

from typing import Optional, Union


class DataPrep:

    def __init__(
            self,
            x,
            y,
            tokenizer: Union[PreTrainedTokenizer, TextVectorization],
            test_size: Optional[float] = 0.2,
            random_state: Optional[int] = None
        )-> None:

        self.x = x
        self.y = y
        self.tokenizer = tokenizer
        self.random_state = random_state

    def data(self):
        return train_test_split(
            self._tokenize(self.x),
            self.y,
            test_size = 0.2,
            random_state = self.random_state
        )     

    
    def _tokenize(self, x):
        if isinstance(self.tokenizer, TextVectorization):
            return self.tokenizer.call(x)
        
        elif isinstance(self.tokenizer, PreTrainedTokenizer):
            return self.tokenizer.tokenize(
                x,
                padding=True,
                truncation=True,
                return_tensors="tf"
            )
        
        else:
            raise NotImplementedError(
                f"Not implemented for tokenizer of type: {type(self.tokenizer)}"
            )