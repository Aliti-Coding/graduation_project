import pandas as pd
import numpy as np
import pathlib
import re
import os

np.random.seed(0)


def extract_transform_amazon_reviews(filepath:str, outpath:str=None, features:list=None, chunksize:int=500000, chunks_to_load:int=1, max_words:int=150) -> None:
    """
    Extract and transform amazon reviews dataset to new csv file.

    The transformations are as follows:
        - Load the chunk
        - Balance number of negative and positive reviews
        - Remove null values
        - Remove reviews with no text
        - Cut reviews to maximum length
        - Convert datecolumn to datetime

    Total loaded/transformed rows equals `chunksize * chunks_to_load`.

    Each loaded and transformed chunk is stored as a partitioned csv file.

    ## NOTE:
    This functions doesn't remove punctuation and convert text to lowercase, responsibility of tokenizer in ML workloads.

    ## Params:
    filepath: path,
        Path to amazon reviews dataset file.

    outpath: path,
        where to save transformed data.
    
    chunksize: pandas chunksize,
        Pandas datafram loader chunksize, should be between 1 and 1,000,000.

    chunks_to_load: num chunks,
        The number of chunks to load, number of total rows equals `chunksize * chunks_to_load`.

    max_words: upper bound,
        The maximum number of words in the reviewText of a review.

    ## Returns:
    None, saved_to_file
    """

    reader = pd.read_json(
        path_or_buf=filepath,
        lines=True,
        chunksize=chunksize
    )

    for chunk_n in chunks_to_load:
        df = reader.__next__()
        df = transform_chunk(df, max_words, features)
        save_chunk(df, datapath=filepath)


def transform_chunk(df, features:list=None, max_words:int=150) -> pd.DataFrame:
    """
    Transform an extract amazon review chunk.

    """
    if features:
        df = extract_features(df, features)

    df = balance_neg_pos_of_reviews(df)

    df = fill_empty_reviews_convert_to_string(df, "reviewText")

    df = cut_reviews_to_max_words(df, max_words, "reviewText")

    df = remove_empty_reviews(df, "reviewText")

    df = convert_column_to_dt(df, "unixReviewTime", "s")

    return df


def extract_features(df, features:list) -> pd.DataFrame:
    return df.loc[:, features]


def balance_neg_pos_of_reviews(df:pd.DataFrame) -> pd.DataFrame:
    """
    Balances number of positive reviews and negative reviews by undersampling the overrepresented class.

    Neutral, ie. reviews with score of 3 are not balanced, might therefore be overrepresented.

    ## Params:
    df: Pandas DataFrame,
        a Pandas DataFrame containing the raw reviews loaded from csv.
    
    ## Returns:
    Balanced dataframe.

    ## TODO:
    - Neutral reviews should be equal to the average of every other count.
    - Consider oversampling instead of undersampling to balance.
    """
    
    value_counts = df["overall"].value_counts()
    
    count_pos = value_counts[5] + value_counts[4]
    
    count_neg = value_counts[2] + value_counts[1] 
    
    # More positive than negative reviews
    if count_pos > count_neg:
        rows_to_drop = count_pos - count_neg

        # Get indexes of random rows where rating is 4 or 5 (positive)
        index = np.random.choice(
            a=df.query("overall == 4 or overall == 5").index, 
            size=rows_to_drop, 
            replace=False
        )

    # More negative than positive reviews
    elif count_pos < count_neg:
        rows_to_drop = count_neg - count_pos
        
        # Get indexes of random rows where rating is 1 or 2 (negative)
        index = np.random.choice(
            a=df.query("overall == 1 or overall == 2").index, 
            size=rows_to_drop, 
            replace=False
        )

    
    df_balanced = df.drop(
        axis=1,
        index=index
    )

    return df_balanced


def fill_empty_reviews_convert_to_string(df:pd.DataFrame, review_text_column:str="reviewText") -> pd.DataFrame:
    """
    Fill in nan valued reviews with empty strings, then convert the column to string dtype.
    """
    
    df[review_text_column] = (
        df[review_text_column]
        .fillna("")
        .convert_dtypes(convert_string=True)
    )

    return df


def cut_reviews_to_max_words(df:pd.DataFrame, max_words:int, review_text_column:str="reviewText") -> pd.DataFrame: 
    """
    Cuts reviews down to maximum soecified length.
    """

    cut_review_text = lambda x: " ".join(x.split()[:max_words])

    df[review_text_column] = df[review_text_column].apply(cut_review_text)

    return df



def remove_empty_reviews(df:pd.DataFrame, review_text_colum:str="reviewText") -> pd.DataFrame:
    """
    Remove rows where reviews are empty strings.
    """

    df = df.loc[
        df[review_text_colum] != "", :
    ]

    return df


def convert_column_to_dt(df:pd.DataFrame, date_column:str="unixReviewTime", unit:str="s") -> pd.DataFrame:
    """
    Converts the specified column to datetime format
    """
    
    df[date_column] = pd.to_datetime(df[date_column], unit=unit)
    return df


def save_chunk(df, datapath:str=None, outpath:str=None) -> None:
    """
    Saves a loaded chunk/df, named based on `datapath`.

    Either `datapath` or `outpath` must be specified.
    """
    
    if datapath:
        
        path = pathlib.Path(datapath)

        file_name = path.parts[-1].split(".")[0] + f"_partition_rows_{df.index[0]}_{df.index[-1]}"
        
        df.to_csv(f"../../data/transformed/{file_name}.csv")

    elif outpath:
        df.to_csv(outpath)
    
    else:
        df.to_csv(f"backup/data_rows_{df.index[0]}_{df.index[-1]}")
        print("WARNING: datapath or outpath must be specified, df was saved to 'backup'")