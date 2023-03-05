from typing import AnyStr, Type
import re


class StrPlus(str):
    def __init__(
            self, 
            text: object
        ) -> None :
        super().__new__(str, text)
    

    def letters(
            self,
            repl:str = " "
        ) -> 'StrPlus':

        return re.sub(r"[^a-zA-Z]", repl, self)

    def alphanumeric(
            self,
            repl:str = " "
        ) -> 'StrPlus':

        return re.sub(r"[^a-zA-Z0-9]", repl, self)
    
    def one_space(self):
        return re.sub(r" +", " ", self)

    def sentences(
            self,
            symbols: str = r"!?.%",
            keep_symbols: bool = False, 
        ):

        n_pattern = "\\"
        for idx,sb in enumerate(symbols):
            n_pattern += sb
            if idx != len(symbols)-1:
                n_pattern += "|"
                n_pattern += "\\"
        
        print(n_pattern)
        if keep_symbols:
            pattern = fr"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<={n_pattern})\s" 
            # pattern = fr"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s" 
        
        return re.split(pattern, self)
    


s = StrPlus("hello. Is this a dream? it must be! bahaha%")
print(s.sentences(keep_symbols=True))