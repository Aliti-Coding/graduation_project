import pandas as pd
import numpy as np
from numpy.random import RandomState
import os
from pathlib import Path

from pandas.io.json._json import JsonReader

from typing import List, Optional, Union, Callable

import pyarrow as pa
import pyarrow.json
import pyarrow.compute
import pyarrow.parquet

class ArrowAmazonReviewsExtractor:
    """
    AmazonReviewsExtractor, extracts and transforms amazon reviews like [these](https://nijianmo.github.io/amazon/index.html).

    Class is based on and inherits from pandas.JsonReader.

    """

    def __init__(
            self,
            path_or_buf: Union[str, os.PathLike],
            blocksize: int = 100_000,
            max_chunksize: int = 500_000,
            features: Optional[List[str]] = None,
            maximum_words: Optional[int] = None,
            review_text_columnn: str = "reviewText",
            drop_empty_reviews: bool = True,
            ratings_column: str = "overall",
            balance_num_pos_neg_ratings: bool = True,
            balance_neutral_reviews: bool = False,
            convert_dates: Optional[List[str]] = ["unixReviewTime"],
            outdir: Optional[Union[str, os.PathLike]] = None,
            save_method: Optional[Callable[[pd.DataFrame, os.PathLike], None]] = None
        ) -> None:

        """
        If possible convert_dates should never be called on the column `"reviewTime"` as pandas struggles to parse it, use `"unixReviewTime"` instead.    
        

        Does not support chunking, meaning entire dataset must fit in memory. However, very effective on datasets up tp 3 million rows, about 300 MBs.
        WARNING: Work in progress.
        
        ## Params
        """

        
        self.json_read_opts = pa.json.ReadOptions(
            use_threads = True,
            block_size = blocksize if blocksize else 100_000
        )
        
        self.path_or_buf = Path(path_or_buf)
        self.blocksize = blocksize
        self.max_chunksize = max_chunksize
        self.features = features
        self.maximum_words = maximum_words
        self.review_text_column = review_text_columnn
        self.drop_empty_reviews = drop_empty_reviews
        self.ratings_column = ratings_column
        self.balance_num_pos_neg_rating = balance_num_pos_neg_ratings
        self.balance_neutral_reviews = balance_neutral_reviews
        self.convert_dates = convert_dates
        self.outdir = outdir
        self.save_method = save_method

        self._loaded_chunks = 0
        self._is_data_loaded = False

        self._rs = RandomState(0)
        

    
    def load(self) -> Union[pa.Table, None]:
        if not self._is_data_loaded:
            self.data = pa.json.read_json(
                self.path_or_buf,
                self.json_read_opts
            )
            
            if self.features:
                columns_to_drop = set(data.column_names).difference(set(self.features))
                data = data.drop(columns_to_drop)

            if self.outdir():
                pa.parquet.write_dataset(
                    table = self.data,
                    root_path = self.outdir,
                    partition_columns = [self.ratings_column]
                )
            else:
                return self.data
            
        else:
            print("Data has already been loaded! Check: '.data'")

            self.reader = data.to_reader(max_chunksize = self.max_chunksize)
        
        batch = self.reader.read_next_batch()

    
    def transform(self) -> Union[pa.Table, None]:
        data = pa.json.read_json(self.json_read_opts)
        
        if self.outdir:
            self._save(self._transform(data))

        elif not self.outdir:
            return self._transform(data)


    def _transform_batch(self, record_batch: pa.RecordBatch) -> pa.Table:
        """
        The main transformation pipe.
        """

        if self.balance_num_pos_neg_rating:
            record_batch = self._balance_reviews(df)

        if self.review_text_column:
            mask = pa.compute.is_null(
                record_batch[self.review_text_column]).combine_chunks()
            
            if self.drop_empty_reviews:
                record_batch = ...
            elif not self.drop_empty_reviews:
                record_batch

            record_batch[self.review_text_column] = pa.compute.replace_with_mask(
                record_batch[self.review_text_column], mask, "")
            

        if self.maximum_words:
            df[self.review_text_column] = df[self.review_text_column].apply(
                lambda x: " ".join(x.split())[:self.maximum_words]
            )

        if self.drop_empty_reviews:
            df = df.loc[df[self.review_text_column] != "",:]

        # Might improve performance in some rare cases, commented out for convenience
        # Parsing dates directly in JsonReader is a bit faster 
        # if self.convert_dates:
        #     for column in self.convert_dates:
        #         df[column] = pd.to_datetime(df[column])
        
        return df