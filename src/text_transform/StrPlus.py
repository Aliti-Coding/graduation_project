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
            qstn_mark: bool = True,
            excl_mark: bool = True,
            period: bool = True,
            comma: bool = False,
            keep_punctuation: bool = False,
            symbols: str = None
        ):
        pattern = r""
        if qstn_mark: pattern += "?"
        if excl_mark: pattern += "!"
        if period: pattern += "."
        if comma: pattern += ","
        if symbols: pattern += symbols

        pattern = fr"[{pattern}] "
        
        if keep_punctuation:
            pattern = fr"({pattern})" 
        
        return re.split(pattern, self)