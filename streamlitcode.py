# Importing the dependecies

import tweepy                             # API for getting twitter info
import pandas as pd
import matplotlib.pyplot as plt
import re
from textblob import TextBlob             # To analyse the sentiment
from wordcloud import WordCloud,STOPWORDS # To make a wordcloud
import datetime
import streamlit as st
import plotly.express as px


# Adding streamlit features to webpage

st.set_page_config(layout="wide")
st.markdown("<center><font size=6><b>Twitter Sentiment Analysis</b></font></center>",unsafe_allow_html=True)
st.subheader("Introduction")
st.markdown("Hi, my name is Chirag Gupta and I'm a Data Science enthusiast. You can connect with me on <a href='https://www.linkedin.com/in/chirag-gupta-359593218/'>LinkedIn</a>.",unsafe_allow_html=True)
st.markdown("Approximately 500 million tweets are posted everyday on Twitter. No matter what happens in this world, Twitter is the first place people go to write about an event. Thus it has become so crucial to know what a person feels about a specific topic and analyze the sentiment behind those tweets.")
st.markdown("This is my first project on API and Sentiment Analysis and it has been made possible with the help of a Twitter Developer Account. Apply for your own <a href='https://developer.twitter.com/en/apply-for-access'>Twitter Developer Account</a>.",unsafe_allow_html=True)
st.markdown("Go ahead and try out this not so amazing app I made for you. It may not be fast and effiecient, but ehh it does the work, so please bear with a newbie coder and have patience. Thank you.")
st.warning('This app is currently down due to the Twitter API limitations for the unpaid version.')
st.markdown("***")


# Storing the API KEYS provided by Twitter Dev Account

api_key             = st.secrets['api_key']
api_secret_key      = st.secrets['api_secret_key']
access_token        = st.secrets['access_token']
access_token_secret = st.secrets['access_token_secret']


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

#@st.cache
def get_user_inputs(hashtag,num_of_tweets,until):
    
    global tweets
    global created_at
    tweets = []
    created_at = []
    bar = st.progress(0)
    progress = 1
    total_days = until

    searchword = hashtag+'-filter:retweets AND -filter:replies'
    today = datetime.date.today()
    
    for i in range(until,0,-1):
        delta = datetime.timedelta(days = until-2)
        until_date = today - delta
        formatted_date = until_date.strftime("%Y-%m-%d")
        until = until - 1
        get_tweets(searchword,formatted_date,num_of_tweets)
        bar.progress(int((100*progress/total_days)))
        progress = progress + 1

    st.success("Tweets Fetched Successfully")

def create_df():
    data = {"Tweet":tweets,
        "Date":created_at}
    dummy = pd.DataFrame(data)

    dummy['Tweet'] = dummy['Tweet'].apply(lambda x:cleaned_tweet(x))
    dummy['Polarity'] = dummy['Tweet'].apply(lambda x:calculate_polarity(x))
    dummy.drop_duplicates(inplace=True)

    dummy.loc[dummy['Polarity'] > 0, "Sentiment"] = "Positive"
    dummy.loc[dummy['Polarity'] == 0, "Sentiment"] = "Neutral"
    dummy.loc[dummy['Polarity'] < 0, "Sentiment"] = "Negative"

    return dummy


# Getting user Inputs and Creating the dataframe

tweets = []
created_at = []

col1,col2,col3 = st.columns((2,1,2))
col1.text_input("Search a keyword :", key="hashtag")
col1.markdown("<br><br>",unsafe_allow_html=True)
hashtag = st.session_state.hashtag
num_of_tweets = col3.radio('Select the number of tweets that must be scraped per day :',(50,100,150,200))
col3.markdown("<br><br>",unsafe_allow_html=True)
until = col1.slider("Select the number of days until the tweets must be scraped :",min_value=1,max_value=10)

if col3.button('Fetch Tweets'):
    with st.spinner("Fetching Tweets. Please Wait..."):
        get_user_inputs(hashtag,num_of_tweets,until)

    initial_df = create_df()
    df = initial_df.copy()
    pos = df[df['Sentiment']=='Positive']
    neg = df[df['Sentiment']=='Negative']


    # Pie Chart for Positive and Negative Tweets

    labels = ['Positive','Negative']
    values = [pos.shape[0],neg.shape[0]]
    fig = px.pie(values=values,names=labels,title="Positive and Negative Tweet Pie Chart",color_discrete_sequence=['#61ff69','#ff6961'])
    st.write(fig)


    # Line Plot

    df_day = df.groupby([pd.Grouper(key='Date', freq='D'), 'Sentiment']).size().unstack('Sentiment')
    df_day.index = df_day.index.strftime('%Y-%m-%d')
    df_day.drop(columns='Neutral',inplace=True)
    fig2 = px.line(df_day,color_discrete_sequence=['#ff6961','#61ff69'],title="Day wise Tweets",markers=True,labels={'value':'Tweets'})
    st.write(fig2)

    # WordCloud

    twitter_mask = plt.imread("./twitter_mask.jpg")

    # For Positive Tweets
    text = " ".join(tweet for tweet in pos['Tweet'])
    wc = WordCloud(background_color="white", max_words=500, mask=twitter_mask, stopwords=STOPWORDS)
    wc.generate(text)
    fig3 = px.imshow(wc,title="WordCloud for Positive Tweets",width=980,height=900)
    fig3.update_layout(coloraxis_showscale=False)
    fig3.update_xaxes(showticklabels=False)
    fig3.update_yaxes(showticklabels=False)
    st.write(fig3)

    # For Negative Tweets
    text = " ".join(tweet for tweet in neg['Tweet'])
    wc = WordCloud(background_color="white", max_words=500, mask=twitter_mask, stopwords=STOPWORDS)
    wc.generate(text)
    fig4 = px.imshow(wc,title="WordCloud for Negative Tweets",width=980,height=900)
    fig4.update_layout(coloraxis_showscale=False)
    fig4.update_xaxes(showticklabels=False)
    fig4.update_yaxes(showticklabels=False)
    st.write(fig4)


    # Display df

    with st.expander("Display Dataframe"):
        st.write(df)
