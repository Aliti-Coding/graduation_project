
from transformers import PreTrainedTokenizer, PreTrainedTokenizerFast
from sklearn.model_selection import train_test_split
from keras.layers import TextVectorization

from typing import Optional, Union, Tuple, Iterable, Any


class DataPrep:

    def __init__(
            self,
            x,
            y,
            tokenizer: Union[PreTrainedTokenizer, TextVectorization],
            test_size: Optional[float] = 0.2,

            random_state: Optional[int] = None,
            max_length: Optional[int] = None
        )-> None:

        self.x = x
        self.y = y
        self.tokenizer = tokenizer
        self.random_state = random_state
        self.test_size = test_size
        self.max_length = max_length

    def data(self) -> Tuple[Iterable[Any], Iterable[Any], Iterable[Any], Iterable[Any]]:
        x_train, x_test, y_train, y_test = train_test_split(
            self.x,
            self.y,
            test_size = self.test_size,
            random_state = self.random_state
        )

        x_train = self._tokenize(x_train)
        x_test = self._tokenize(x_test)

        return x_train, x_test, y_train, y_test

    
    def _tokenize(self, x):
        if isinstance(self.tokenizer, TextVectorization):
            return self.tokenizer.call(x)
        
        elif (
            isinstance(self.tokenizer, PreTrainedTokenizer)
            or
            isinstance(self.tokenizer, PreTrainedTokenizerFast)
        ):
            return dict(self.tokenizer(
                x,
                padding=True,
                truncation=True,
                return_tensors="tf",
                max_length=self.max_length
            ))
        else:
            raise NotImplementedError(f"Not implemented for tokenizer of type: {type(self.tokenizer)}")
           