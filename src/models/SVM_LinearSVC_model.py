import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from tfidf_functions import clean_data, review_to_words
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, classification_report



fp = "Books_5_partition_1.csv"
df_orig = pd.read_csv(fp)
# remove null values and reset index so we get the same shape as the list returned from the clean_data function
df_orig = df_orig.dropna()
df_orig = df_orig.reset_index(drop=True)

df_orig.columns
df_orig['overall'].shape

#______________________________________________________________________________________________________________
df = df_orig.copy()

#preprocessing
df['preprocessed'] = clean_data(fp)


#removing number 3 rating, as it is considered neutral, main focus now is positiv and negativ
df=df[df['overall'] != 3]
df['label'] = df['overall'].apply(lambda x: 1 if x >=4 else 0) # applies 4&5 label 1 and 1&2 label 0


df['label'].value_counts() #50/50 positiv/negativ


X_train, X_test, y_train, y_test = train_test_split(df['preprocessed'], df['label'], test_size=0.2, random_state=420)

print(f"Train: ,{X_train.shape,y_train.shape},Test: ,{X_test.shape,y_test.shape}")


vectorizer = TfidfVectorizer()
tf_x_train = vectorizer.fit_transform(X_train)
tf_x_test = vectorizer.transform(X_test)

print(tf_x_train.shape)
print(tf_x_test.shape)


# implementing SVM
clf = LinearSVC(random_state=0)

clf.fit(tf_x_train, y_train)

y_train_pred = clf.predict(tf_x_train)
y_test_pred = clf.predict(tf_x_test)

x_test_accuracy = accuracy_score(y_test, y_test_pred)
print(f"test accuracy:  {x_test_accuracy}")

x_train_accuracy = accuracy_score(y_train, y_train_pred)
print(f"train accuracy:  {x_train_accuracy}")


report_test = classification_report(y_test, y_test_pred, output_dict=True)
df_report_test = pd.DataFrame(data=report_test)
df_report_test
