import numpy as np
import os
import pandas as pd
import json
import nltk
import pandas as pd
# function to preprocess
import re
import string
#library that contains punctuation
import csv
nltk.download('wordnet')
nltk.download("punkt")
from nltk.stem import WordNetLemmatizer
# defining the object for Lemmatization
wordnet_lemmatizer = WordNetLemmatizer()
# Stop words removal
# importing nlp library
nltk.download('stopwords')
# Stop words present in the library
stopwords = nltk.corpus.stopwords.words('english')

def remove_punctuation(s):
    translator = str.maketrans(string.punctuation, ' '*len(string.punctuation)) #map punctuation to space
    return s.translate(translator)

def lemmatizer(text):
    lemm_text = " ".join([wordnet_lemmatizer.lemmatize(word) for word in nltk.word_tokenize(text)])
    return lemm_text

#defining the function to remove stopwords from tokenized text
def remove_stopwords(text):
    output= " ".join([i for i in nltk.word_tokenize(text) if i not in stopwords])
    return output

def transform_function(statements):
    all_rows = []
    for row in statements:
        row = remove_stopwords(row)
        row = remove_punctuation(row)
        row = lemmatizer(row)
        row = " ".join(nltk.word_tokenize(row.lower()))
        all_rows.append(row)
    return all_rows    

def input_fn(input_data, request_content_type):
    if request_content_type == "application/json":
        sentence = json.loads(input_data)
        return sentence["instances"]
    else:
        raise ValueError(f"{request_content_type} not supported")


def predict_fn(input_data, model):
# featurizer model is only for transforming features
#     if label_column in input_data:
#         raw_features = input_data.drop(label_column, axis=1)
#     else:
#         raw_features = input_data
    return transform_function(input_data)
    

# returning in the format suitable for the blazing text
def output_fn(prediction, response_content_type):
    return {"instances" : prediction, "configuration": {"k": 1}}


def model_fn(model_dir):
#     not required
#     preprocessor = joblib.load(os.path.join(model_dir, "model.joblib"))
    return 1
