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
        
        Time complexity to load and transform grows more than proportionally with chunksize ie. two chunks of 500_000 rows loads faster than one at 1_000_000 rows.
        
        ## Params
        path_or_buf: pathlike,
            path to file to load data from, should be `.json`,
            can be compressed as long as pandas is able to infer compression type.

        chunksize: int,
            the size of each chunk to load from data source (`path_or_buf`).

        features: list of feature names, optional,
            the features to extract from each chunk/DataFrame, 
            might have downstream effects on pipeline depending on what is included.

        maximum_words: int, optional,
            if specified sets the maximum number of words a reviewText can have, 
            longer are cut to length of maximum_words.
        
        review_text_column: str,
            specifies which column contains the reviews text. Default is "reviewText".

        drop_empty_reviews: bool,
            drop rows where reviews only contain empty strings.

        ratings_column: str,
            specifies the name of the column that contains the ratings of the reviews. 
            Default is "overall".
        
        balance_num_pos_neg_ratings: bool,
            undersampling so that the total number of positive (`rating>3`) and negative (`rating<3`) reviews are equal.
            The ratings column and review text column must be in the DataFrame.

        balance_neutral_reviews: bool,
            balance the number of neutral reviews (`rating==3`) to the average of negative and positive reviews.

        convert_dates: bool or list[str],
            optimistic if using bool, or specify the names of columns to convert to datetime objects.

        outdir: pathlike, optional,
            if specified overloads iterator functionality, 
            now saves each chunk to `outdir` instead of returning a DataFrame.
        
        save_method: function or callable, optional,
            if not specified chunks are saved as `.parquet` files. Use this variable to save chunks in other file formats.
            The callable should take two arguments a `DataFrane` and a `PathLike` used to overide saving method.


        ## Examples

        Example `save_method` function: 
            >>> lambda df, path: pd.DataFrame.to_json(df, path)

        

        
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


    def _balance_reviews(
            self, 
            df: pd.DataFrame
        ) -> pd.DataFrame:

        """
        TODO:
        - Implement option for oversampling.
        - Alpha property which determines the ratio of undersampling to oversampling.

        Balances the number of negative and positive reviews in a chunk 
        if `balance_num_neg_pos_reviews` is `True` by undersampling.

        Balances the number of neutral reviews if `balance_neutral` is `True`, 
        by undersampling.
        """

        if not (
            self.ratings_column in df.columns \
            and \
            self.review_text_column in df.columns
        ):
            raise ValueError("Ratings column and review text column must be in DataFrame to balance reviews.")

        value_counts = df[self.ratings_column].value_counts()
        num_positive = value_counts[4] + value_counts[5]
        num_negative = value_counts[1] + value_counts[2]

        if num_positive > num_negative:
            rows_to_drop = num_positive - num_negative

            index = self._rs.choice(
                a=df.query("overall == 4 or overall == 5").index, 
                size=rows_to_drop, 
                replace=False
            )
        
        elif num_negative > num_positive:
            rows_to_drop = num_negative - num_positive
            
            index = self._rs.choice(
                a=df.query("overall == 1 or overall == 2").index, 
                size=rows_to_drop, 
                replace=False
        )

        df_balanced = df.drop(
            axis=1,
            index=index
        )

        if self.balance_neutral_reviews:
            balanced_value_counts = df_balanced[self.ratings_column].value_counts()

            num_neutral = balanced_value_counts[3]
            num_non_neutral = df_balanced[self.ratings_column].count() - num_neutral

            avg_value_count_non_neutral = num_non_neutral / 4

            if num_neutral > avg_value_count_non_neutral:
                rows_to_drop = num_neutral - avg_value_count_non_neutral

                index = self._rs.choice(
                    a=df.query("overall == 3").index, 
                    size=rows_to_drop, 
                    replace=False
                )

                df_balanced = df.drop(
                    axis=1,
                    index=index
                )


        return df_balanced
        
    def _save(
            self, 
            table: pa.Table
        ) -> None:

        """
        Saves the chunk to `self.outdir` if it has been specified.

        Alternatively uses the callable stored in `self.save_method` to save the chunk.
        """
        old_filename = self.path_or_buf.parts[-1].split(".")[0]
        save_path = f"{self.outdir}/{old_filename}_{self._loaded_chunks}"

        if self.save_method:
            self.save_method(df, save_path)
        
        else:
            save_path += ".parquet"
            df.to_parquet(save_path, index=False)