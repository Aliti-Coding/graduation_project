import pandas as pd
from keras.layers import TextVectorization


class Tokenizer(TextVectorization):
    """
    Simple abstract wrapper class for `keras.layers.TextVectorization`.

    The class inherits from the `TextVectorization` class.
    """

    def __init__(
            self, 
            max_tokens:int=15000, 
            sequence_length:int=100, 
            vocabulary=None
        ) -> None:
        
        """
        Construct the tokenizer. This tokenizer strips punctuation and lowercases text.

        ## Params:
        max_tokens: upper limit,
            the maximum number of words to store in the vocabulary.
        
        sequence_length: upper limit,
            the maximum number of words to tokenize in a sequence, the tokenizer outputs `sequence_length` tokens.
        """
        
        super().__init__(
            max_tokens=max_tokens,
            standardize="lower_and_strip_punctuation",
            output_mode="int",
            output_sequence_length=sequence_length,
            vocabulary=vocabulary
        )


    def decode(self, tokens_iterable:list) -> list:
        """
        Decodes input tokens into corresponding words in the tokenizers vocabulary.
        
        Returns an empty string if token not in vocabulary.
        """

        vocabulary = self.get_vocabulary()
        decoded = []

        for tokens in tokens_iterable:
            tmp_decoded = []
            
            for token in tokens:
                
                try:
                    tmp_decoded.append(vocabulary[token])
                
                except IndexError:
                    tmp_decoded.append("")
            
            decoded.append(tmp_decoded)

        return decoded


    @classmethod
    def from_vocabulary_file(cls, filepath:str, sequence_length) -> Tokenizer:
        """
        Construct Tokenizer from a vocabulary file.

        ## Params:
        filepath: path,
            path to vocabulary file
        """

        tokenizer = cls.__init__(sequence_length=sequence_length)
        tokenizer.load_vocabulary(filepath)

        return tokenizer
        


    def save_vocabulary(self, filepath) -> None:
        with open(filepath, "w") as file:
            file.write("\n".join(self.get_vocabulary()))


    def load_vocabulary(self, filepath) -> list:
        with open(filepath, "r") as file:
            vocabulary = file.read().split("\n")

        self.set_vocabulary(vocabulary)