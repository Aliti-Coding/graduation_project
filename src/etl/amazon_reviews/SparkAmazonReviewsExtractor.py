import pandas as pd
import numpy as np
from numpy.random import RandomState
import os
from pathlib import Path

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import (
    StructType, 
    StructField,
    IntegerType, 
    StringType,
    ByteType,
    DateType,
    BooleanType,
    FloatType,
)

from typing import List, Optional, Union, Callable


class SparkAmazonReviewsExtractor:
    """
    AmazonReviewsExtractor, extracts and transforms amazon reviews like [these](https://nijianmo.github.io/amazon/index.html).

    Class is based on and inherits from pandas.JsonReader.

    """

    def __init__(
            self,
            path_or_buf: Union[str, os.PathLike],
            features: Optional[List[str]] = None,
            maximum_words: Optional[int] = None,
            review_text_columnn: str = "reviewText",
            drop_empty_reviews: bool = True,
            ratings_column: str = "overall",
            balance_num_pos_neg_ratings: bool = True,
            balance_neutral_reviews: bool = False,
            convert_dates: Optional[List[str]] = ["unixReviewTime"],
            outdir: Optional[Union[str, os.PathLike]] = None,
        ) -> None:

        """
        WIP
        """        
        self.path_or_buf = Path(path_or_buf)
        self.features = features
        self.maximum_words = maximum_words
        self.review_text_column = review_text_columnn
        self.drop_empty_reviews = drop_empty_reviews
        self.ratings_column = ratings_column
        self.balance_num_pos_neg_rating = balance_num_pos_neg_ratings
        self.balance_neutral_reviews = balance_neutral_reviews
        self.convert_dates = convert_dates
        self.outdir = outdir

        self._loaded_chunks = 0

        self._rs = RandomState(0)

        self.schema = StructType([
            StructField("overall", IntegerType()),
            StructField("verified", BooleanType()),
            StructField("reviewTime", StringType()),
            StructField("reviewerID", StringType()),
            StructField("asin", IntegerType()),
            StructField("reviewerName", StringType()),
            StructField("reviewText", StringType()),
            StructField("summary", StringType()),
            StructField("unixreviewTime", DateType()),
            StructField("style", ByteType()),
            StructField("vote", FloatType()),
            StructField("image", StringType())
        ])

        self.spark_session = SparkSession.builder.getOrCreate()


    def _transform(self, df: DataFrame) -> DataFrame:
        if self.features:
            cur_columns = set(df.columns)
            features_to_keep = set(self.features)
            columns_to_drop = cur_columns.difference(features_to_keep)
        
            df = df.drop(*columns_to_drop)

        if self.drop_empty_reviews:
            df = (
                df.where(f"{self.review_text_column} != ''")
                .where(f"{self.review_text_column} is not null")
            )

        if self.maximum_words:
            ...

        return df

    def _load(self) -> DataFrame:
        df = self.spark_session.read.json(
            path = "./data/raw/Sports_and_Outdoors_5.json.gz",
            schema = self.schema,
            multiLine=False
        )
        
        return df
    
    def _save(self) -> None:
        ...