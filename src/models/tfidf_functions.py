import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
import re
from sklearn.feature_extraction.text import TfidfVectorizer

#function for cleaning data
def review_to_words(raw_review):
    """Removes html tags, everything except letters, 
    and filters out stop words
    example how to use function: \n 
    for i in range(0, len(train['review'])): \n
        clean_train_reviews.append(review_to_words(train['review'][i])).

    Args:
        raw_review (_str_): _input the column you want to transform_

    Returns:
        _str_: _a string that is transformed_
    """
    #1 if any html tags, removed 
    review_text = BeautifulSoup(raw_review, features="lxml").get_text()

    #2 remove puctions and numbers
    letters_only = re.sub("[^a-zA-Z]", " ", review_text)

    #3 convert to lowercase and split
    words_lst = letters_only.lower().split()

    #4 convert stop words to set for increased speed processing
    stops = set(stopwords.words("english"))

    #5 remove stop words from the text
    meaningful_words = [w for w in words_lst if not w in stops] #if w in stops remove it

    #6 transform the list to text string
    meaningful_words_str = " ".join(meaningful_words)

    return meaningful_words_str

    
def clean_data(filepath, num=None):
    """ reads csv file to a dataframe and cleans review column

    Args:
        filepath (_str_): _filepath of the csv file_

    Returns:
        _DataFrame_: _returns a list with clean text with no stopwords_
    """
    df_orig = pd.read_csv(filepath)
    # print(df_orig.isna().sum())
    df_orig = df_orig.dropna()
    df_orig = df_orig.reset_index(drop=True)
    clean_review = [review_to_words(df_orig['reviewText'][row]) for row in range(0, len(df_orig['reviewText']))]
 
    df_orig['preprocessed'] = clean_review
    return df_orig


# finding how many different words there are in the corpus
def words_in_corpus(clean_text):
    """finding how many different words there are in the corpus
    Args:
        clean_text (_list_): _clean-reviews_
    Returns:
        _str_: _number of unique words in the corpus_
    """     

    words_set = set()
    for i in clean_text:
        words = i.split(' ')
        # print(words)
        words_set = words_set.union(set(words))

    return f'number of words in the corpus {len(words_set)}'

# words_in_corpus(clean_data("Books_5_partition_1.csv"))