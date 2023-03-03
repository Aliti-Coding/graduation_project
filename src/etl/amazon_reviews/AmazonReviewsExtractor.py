import pandas as pd
import numpy as np
from numpy.random import RandomState
import os

from pandas.io.json._json import JsonReader

from typing import List, Optional, Union, Callable




class AmazonReviewsExtractor(JsonReader):
    """
    AmazonReviewsExtractor, extracts and transforms amazon reviews like [these](https://nijianmo.github.io/amazon/index.html).

    Class is based on and inherits from pandas.JsonReader.

    """

    def __init__(
            self,
            path_or_buf: Union[str, os.PathLike],
            chunksize: int = 100_000,
            features: Optional[List[str]] = None,
            maximum_words: Optional[int] = None,
            review_text_columnn: str = "reviewText",
            drop_empty_reviews: bool = True,
            ratings_column: str = "overall",
            balance_num_pos_neg_ratings: bool = True,
            balance_neutral_reviews: bool = False,
            convert_dates: Union[bool, List[str]] = ["reviewTime"],
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
            if not specified chunks are saved as `.csv` files. Use this to save chunks in other file formats.
            The callable should take two arguments a `DataFrane` and a `PathLike` which can be overridden for different ways of saving.


        ## Examples

        Example `save_method` function: 
            >>> lambda df, path: pd.DataFrame.to_json(df, path)

        

        
        """
        super().__init__(
            path_or_buf,
            orient = None,
            typ = "frame",
            dtype = None,
            convert_axes = None,
            convert_dates = convert_dates,
            keep_default_dates = True,
            numpy = False,
            precise_float = False,
            date_unit  = None,
            encoding = None,
            encoding_errors = "strict",
            lines = True,
            chunksize = chunksize,
            compression = "infer",
            nrows = None,
            storage_options = None,
        )
        
        self.path_or_buf = path_or_buf
        self.chunksize = chunksize
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

        self._rs = RandomState(0)


    def __next__(self) -> Union[pd.DataFrame, None]:
        """
        Loads next chunk, or loads and saves the next chunk if `outpath` is specified.
        """
        self._loaded_chunks += 1

        df = super().__next__()
        if not self.outdir:
            return self._transform_chunk(df)

        elif self.outdir:
            self._save_chunk(df)
    
    def transform(self, df:pd.DataFrame) -> Union[pd.DataFrame, None]:
        """
        TODO:
        - Function should be callable as a class method
        - Transform based on config or similar
        - Transform without instantiating a class instance manually
        """
        
        raise NotImplementedError


    def extract_n_chunks(self, num_chunks: int = 1):
        """
        TODO:
        - Implement capped iterator, ie. returning an iterator with max num of iterations.
        - Implement automatic saving and transformations when outdir is specified
        """
        
        raise NotImplementedError

        for chunk in range(num_chunks):
            ...


    def _transform_chunk(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        The main transformation pipe of the chunk.
        """

        if self.features:
            df = df.loc[:, self.features]

        if self.balance_num_pos_neg_rating:
            df = self._balance_reviews(df)

        df[self.review_text_column] = (
            df[self.review_text_column]
            .fillna("")
        )

        if self.maximum_words:
            df = df.apply(
                lambda x: " ".join(x.split)[:self.maximum_words]
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

        assert (
            self.ratings_column in df.columns 
            and 
            self.review_text_column in df.columns
        )

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
        
    def _save_chunk(
            self, 
            df: pd.DataFrame
        ) -> None:

        """
        Saves the chunk to `self.outdir` if it has been specified.

        Alternatively uses the callable stored in `self.save_method` to save the chunk.
        """

        save_path = f"{self.outdir}/amazon_reviews_chunk_{self._loaded_chunks}"

        if self.save_method:
            self.save_method(df, save_path)
        
        else:
            save_path += ".csv"
            df.to_csv()