import flask
import tweepy
from textblob import TextBlob
import pandas as pd
import re

application = flask.Flask( __name__, template_folder='templates' )

def login(input_name):
    tweet_login = pd.read_csv('./login/Login.csv')
    consumerKey = tweet_login['keys'][0]
    consumerSecret = tweet_login['keys'][1]
    accessToken = tweet_login['keys'][2]
    accessTokenSecret = tweet_login['keys'][3]
    authenticate = tweepy.OAuthHandler(consumerKey, consumerSecret)
    authenticate.set_access_token(accessToken, accessTokenSecret)
    api = tweepy.API(authenticate, wait_on_rate_limit = True)
    posts = api.user_timeline(screen_name = input_name, count=100, lang = 'en', tweet_mode = 'extended')

    df = pd.DataFrame( [tweet.full_text for tweet in posts], columns=['Tweets'] )

    def textCleaning(text):
        text = re.sub( r'@[A-Za-z0-9]+', "", text )
        text = re.sub( r'#', "", text )
        text = re.sub( r'RT[\s]', "", text )
        text = re.sub( r'https?:\/\/\S+', "", text )
        text = re.sub( r':', "", text )
        return text

    df['Tweets'] = df['Tweets'].apply( textCleaning )

    def subjectivityExtract(text):
        return TextBlob(text).sentiment.subjectivity

    def polarityExtract(text):
        return TextBlob(text).sentiment.polarity

    df['Subjectivity'] = df['Tweets'].apply( subjectivityExtract )
    df['Polarity'] = df['Tweets'].apply( polarityExtract )

    def analysisCol(points):
        if points < 0:
            return 'Negetive'
        elif points == 0:
            return 'Neutral'
        else:
            return 'Positive'

    df['Nature of Tweet'] = df['Polarity'].apply( analysisCol )

    positiveTweet = df[df['Nature of Tweet'] == 'Positive']
    positivePer = round( positiveTweet.shape[0] / df.shape[0] * 100, 1 )

    negetiveTweet = df[df['Nature of Tweet'] == 'Negetive']
    negetivePer = round( negetiveTweet.shape[0] / df.shape[0] * 100, 1 )

    neutralTweet = df[df['Nature of Tweet'] == 'Neutral']
    neutralPer = round( neutralTweet.shape[0] / df.shape[0] * 100, 1 )

    return positivePer, negetivePer, neutralPer

# Set up the main route
@application.route( '/', methods=['GET', 'POST'] )
def main():
    if flask.request.method == 'GET':
        return flask.render_template('index.html')

    if flask.request.method == 'POST':
        input_name = flask.request.form['tweet_name']
        final_result = login(input_name)
        return flask.render_template('result.html', analysis_result = final_result, search_name=input_name)

if __name__ == '__main__':
    application.run()