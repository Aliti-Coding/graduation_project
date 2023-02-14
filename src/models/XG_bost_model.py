import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from tfidf_functions import clean_data, review_to_words
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, classification_report, mean_absolute_error, mean_squared_error
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import xgboost as xgb
from xgboost import XGBClassifier
import matplotlib.pyplot as plt
from nltk.sentiment import SentimentIntensityAnalyzer

fp = "Books_5_partition_1.csv"

#getting data and preprocessing it
df = clean_data(fp) # returns a dataframe with a colum were textReview is cleaned
df = df[:50000]
df['overall'].value_counts()

#applying minmax on stars 
MM_scaler = MinMaxScaler()
MM_transformed = MM_scaler.fit_transform(df[['overall']])
df['overall_sc'] = MM_transformed


df['overall_sc'].hist(bins=50)
plt.show()

# slices the reviews in postiv/neutral/negativ
df['sentiment'] = df['overall'].apply(lambda x: 2 if x > 3 else 0 if x < 3 else 1)


vectorizer = TfidfVectorizer(
    max_features= 1000, 
    min_df = 5,
    ngram_range= (1,3)
)
vectors = vectorizer.fit_transform(df['preprocessed'])
dense = vectors.toarray()


X = dense
Y = df['sentiment']

X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=420)
print(f"Train: ,{X_train.shape,y_train.shape},Test: ,{X_test.shape,y_test.shape}")



model = XGBClassifier(
    # max_depth=8, 
    # early_stopping_rounds = 15,
    # learning_rate=0.3, 
    # objective='reg:squarederror'
    )
    
model.fit(X_train, y_train, eval_set = [(X_test, y_test)])

y_train_pred = model.predict(X_train)
y_test_pred = model.predict(X_test)



r2_train_score = model.score(X_train, y_train)
print(f'Train R2 XG : {r2_train_score}')
print()
mse_train_xg = mean_squared_error(y_train, y_train_pred)
print(f'Train MSE XG : {np.sqrt(mse_train_xg)}') 
print()
mae_train_xg = mean_absolute_error(y_train, y_train_pred)
print(f'Train MAE XG : {mae_train_xg}\n') 



r2_test_score = model.score(X_test, y_test)
print(f'Test R2 XG : {r2_test_score}')
print()
mse_test_xg = mean_squared_error(y_test, y_test_pred)
print(f'Test MSE XG : {np.sqrt(mse_test_xg)}') 
print()
mae_test_xg = mean_absolute_error(y_test, y_test_pred)
print(f'Test MAE XG : {mae_test_xg}') 
#test




