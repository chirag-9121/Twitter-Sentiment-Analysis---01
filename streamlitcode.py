# Importing the dependecies

import tweepy                             # API for getting twitter info
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import os                                 # To get the api keys stored as environment variables
from textblob import TextBlob             # To analyse the sentiment
from wordcloud import WordCloud,STOPWORDS # To make a wordcloud
from dotenv import load_dotenv            # For loading the environment variables
import datetime
import streamlit as st

load_dotenv()


# Storing the API KEYS provided by Twitter Dev Account

api_key             = os.getenv('api_key')
api_secret_key      = os.getenv('api_secret_key')
access_token        = os.getenv('access_token')
access_token_secret = os.getenv('access_token_secret')


# Authorizing the API

auth = tweepy.OAuthHandler(api_key,api_secret_key)
auth.set_access_token(access_token,access_token_secret)
api = tweepy.API(auth)


# Functions

def cleaned_tweet(txt):
    return " ".join(re.sub("([^0-9A-Za-z \t])|(\w+:\/\/\S+)", "",txt).split())

def calculate_polarity(tweet):
    blob = TextBlob(tweet)
    return blob.sentiment.polarity

def get_tweets(searchword,formatted_date,num_of_tweets):
    for tweet in tweepy.Cursor(api.search_tweets,q=searchword,tweet_mode='extended',lang='en',result_type='recent',until=formatted_date).items(num_of_tweets):
        tweets.append(tweet.full_text)
        created_at.append(tweet.created_at)

def get_user_inputs():
    
    global tweets
    global created_at
    tweets = []
    created_at = []

    hashtag = input("Search a keyword :")
    searchword = hashtag+'-filter:retweets AND -filter:replies'
    
    num_of_tweets = int(input("Enter number of tweets that must be scraped per day :"))    
    
    today = datetime.date.today()
    until = int(input("Enter number of days until the tweets must be scraped :"))
    
    for i in range(until,0,-1):
        delta = datetime.timedelta(days = until-2)
        until_date = today - delta
        formatted_date = until_date.strftime("%Y-%m-%d")
        until = until - 1
        get_tweets(searchword,formatted_date,num_of_tweets)

# Getting user Inputs

tweets = []
created_at = []
get_user_inputs()


# Creating and Manipulating the dataframe

data = {"Tweet":tweets,
        "Date":created_at}
dummy = pd.DataFrame(data)

df = dummy.copy()
df['Tweet'] = df['Tweet'].apply(lambda x:cleaned_tweet(x))
df['Polarity'] = df['Tweet'].apply(lambda x:calculate_polarity(x))
df.drop_duplicates(inplace=True)

df.loc[df['Polarity'] > 0, "Sentiment"] = "Positive"
df.loc[df['Polarity'] == 0, "Sentiment"] = "Neutral"
df.loc[df['Polarity'] < 0, "Sentiment"] = "Negative"

pos = df[df['Sentiment']=='Positive']
neg = df[df['Sentiment']=='Negative']


# Adding to webpage

st.set_page_config(layout="wide")
st.title('Twitter Sentimental Analysis')
st.markdown("***")

# Pie Chart for Positive and Negative Tweets

plt.figure(figsize=[10,5])
labels = ['Positive','Negative']
values = [pos.shape[0],neg.shape[0]]
plt.pie(values, labels=labels, autopct='%1.2f%%',colors=['#61ff69','#ff6961'])
st.write(plt.show())