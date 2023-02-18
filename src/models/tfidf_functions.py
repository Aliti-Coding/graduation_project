import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
import re
from sklearn.feature_extraction.text import TfidfVectorizer

#1 
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
    review_text = BeautifulSoup(raw_review).get_text()

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


#2
#function that calls the function above and return cleaned strings with no stopwords
def clean_data(raw_text):
    """ reads a pd.Series and cleans the text

    Args:
        filepath (_pd.Series_): Series with 
        text that needs to be cleaned_

    Returns:
        _List_: _returns a list with clean text with no stopwords_
    """

    # df_orig = pd.read_csv(filepath)
    # print(df_orig.isna().sum())
    raw_text = raw_text.dropna()
    raw_text = raw_text.reset_index(drop=True)
    clean_text = [review_to_words(raw_text[row]) for row in range(0, len(raw_text))]
    return clean_text

#3
#creating the tf-idf model
def tf_idf_model(cleaned_text):
    """Takes cleaned text and returns a sparse matrix
    with the feature names

    Args:
        cleaned_text (_list_): _takes the list from function 2 above_

    Returns:
        _np.array_ and _list_: _returns a array with tf-idf scores and a list with feature names(vocabulary)_
    """
    #tf-idf-model
    vectorizer = TfidfVectorizer(
    max_features= 1000, # Selects most frequent words in the corpus when computing the TF-IDF. useful for performance if you have large datasets
    # max_df=  0.8, # removes words that appears 80% in the text.
    min_df = 5, # removes word that appears less than 5 times
    ngram_range= (1,1), #is range to capture the conext and meaning of words. means it checks 3 words at a time.
    )

    vectors = vectorizer.fit_transform(cleaned_text)
    feature_names = vectorizer.get_feature_names_out() #feature names that are most frequent. you can changes this in the max_feature parameter when using TfidfVectorizer
    # print(feature_names)
    dense = vectors.toarray() # returns a sparse matrix with shape (rows * feature_names)

    return dense, feature_names


#4
#function to return the top 5 word with highest idf. 
#function is used on function 5
def get_top_words(row, n=5):
    """This function is used to extract
    the tf-idf scores

    """

    # Get the n largest values and their corresponding column labels
    row = row[row>0]
    top_n = row.nlargest(n)

    # Extract the column labels (i.e., the word names)
    top_words = top_n.index.tolist()
    return top_words


#5 
# function calls on clean data to get cleaned text
# then we call the tf-idf function and use cleaned text as argument on tf-idf function
# last part is to get top 5 words and return a Dataframe
def hottest_word(column_raw_text):
    """Returns a DataFrame with 5 columns that are the hottests words

    Returns:
        _DataFrame_: _DataFrame with 5 hottest_word_
    """

    cleaned_text = clean_data(column_raw_text)
    
    hottest_word_vector, feature_names = tf_idf_model(cleaned_text)
    

    hottest_word_vector = hottest_word_vector.tolist()
    # print(hottest_word_vector)

    df_vector = pd.DataFrame(hottest_word_vector, columns=feature_names)

    top_words = df_vector.apply(get_top_words, axis=1)
    
    df_hottest_word = pd.DataFrame()
    df_hottest_word['hottest_word_1'] = top_words.apply(lambda x: x[0] if len(x) > 0 else None)
    df_hottest_word['hottest_word_2'] = top_words.apply(lambda x: x[1] if len(x) > 1 else None)
    df_hottest_word['hottest_word_3'] = top_words.apply(lambda x: x[2] if len(x) > 2 else None)
    df_hottest_word['hottest_word_4'] = top_words.apply(lambda x: x[3] if len(x) > 3 else None)
    df_hottest_word['hottest_word_5'] = top_words.apply(lambda x: x[4] if len(x) > 4 else None)

    return df_hottest_word




#_________________________________________________________________________________________________________________________________________


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

