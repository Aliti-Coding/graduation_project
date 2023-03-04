from src.text_transform import StrPlus
from typing import AnyStr

class TextPredictor:
    def __init__(
            self,
            model,
            tokenizer,
            split_sentences: bool = True
        ) -> None:

        self.model = model
        self.tokenizer = tokenizer
        self.split_sentences = split_sentences

    def predict(
            self,
            text: AnyStr,   
        ) -> float:

        if self.split_sentences:
            text = StrPlus(text)
            sentences = text.sentences()

            return {
                "text":sentences, 
                "sentiment":[
                    self.model(self.tokenizer(s)) for s in sentences
                ]
            }

        
        else:
            return {
                "text":text,
                "sentiment":self.model(self.tokenizer(text))
            }