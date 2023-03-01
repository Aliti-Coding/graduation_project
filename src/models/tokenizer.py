import pandas as pd
from keras.layers import TextVectorization


class Tokenizer(TextVectorization):


    def __init__(self, max_tokens=15000, sequence_length=100, vocabulary=None):
        """
        Construct the tokenizer. This tokenizer strips punctuation and lowercases text.

        ## Params:
        max_tokens: upper limit,
            the maximum number of words to store in the vocabulary.
        
        sequence_length: upper limit,
            the maximum number of words to tokenize in a sequence, the tokenizer outputs `sequence_length` tokens.
        """

        self.max_tokens = max_tokens
        self.sequence_length = sequence_length

        self.tokenizer = TextVectorization(
            max_tokens=self.max_tokens,
            standardize="lower_and_strip_punctuation",
            output_mode="int",
            output_sequence_length=self.sequence_length,
            vocabulary=vocabulary
        )
    

    def decode(self, tokens_iterable:list) -> list:
        """
        Decodes input tokens into corresponding words in the tokenizers vocabulary.
        
        Returns an empty string if token not in vocabulary.
        """

        vocabulary = self.tokenizer.get_vocabulary()
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
    def from_vocab_file(cls, filepath:str, sequence_length):
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
            file.write("\n".join(self.tokenizer.get_vocabulary()))


    def load_vocabulary(self, filepath) -> list:
        with open(filepath, "r") as file:
            vocabulary = file.read().split("\n")

        self.tokenizer.set_vocabulary(vocabulary)