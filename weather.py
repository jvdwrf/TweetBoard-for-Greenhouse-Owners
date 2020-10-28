# do all necessary imports
from eca import *
from eca.generators import start_offline_tweets
import random
import eca.http
import datetime
import textwrap
import re

# add http POST even handler for /api/filter
def add_request_handlers(httpd):
    httpd.add_route('/api/filter', eca.http.GenerateEvent('filter'), methods=['POST']) 

# initialisition event
@event('init')
def setup(ctx, e):
    # set filter as empty string
    ctx.filter = ""   
    # start the tweet reading from weer.txt  
    start_offline_tweets('weer.txt', time_factor=10000, event_name='read_tweet')

# event when a tweet gets read
@event('read_tweet')
def read_tweet(ctx, e):
    tweet = e.data
    text = textwrap.fill(tweet['text'],initial_indent='    ', subsequent_indent='    ') #text inside tweet
    screen_name = tweet['user']['screen_name']

    # if screen_name = wska_nl, then it contains weather information, and we emit the data inside to the correct charts.
    if(screen_name == "wska_nl"):
        # regex to match for all numbers
        numsInTweet = re.findall(r"\d+,\d+", text)

        # regex to match numbers to floats
        floatsInTweet = list(map(lambda x: float(x.replace(',','.')), numsInTweet))

        Temperature = floatsInTweet[0]
        Humidity = int(re.findall(r"\d+(?=\%)", text)[0]) # 
        Wind_speed = floatsInTweet[1]
        Pressure = floatsInTweet[2]
        Rain = floatsInTweet[3]
        Uv = floatsInTweet[4]

        # 0 values don't get charted, so if the data = 0, set it to 0.000001
        if(Rain == 0): Rain = 0.000001
        if(Temperature == 0): Temperature = 0.000001
        if(Uv == 0): Uv = 0.000001
        if(Wind_speed == 0): Wind_speed = 0.000001

        # emit the right data, to the right chart
        emit('temp', {'action': 'add', 'value': Temperature})
        emit('sun', {'action': 'add', 'value': Uv})
        emit('hum', {'action': 'add', 'value': Humidity})
        emit('press', {'action': 'add', 'value': Pressure})
        emit('wind', {'action': 'add', 'value': Wind_speed})
        emit('rain', {'action': 'add', 'value': Rain})

    # else, if the filter is found in the tweet, emit the tweet
    elif(ctx.filter in text):
        emit('tweet', tweet)    


# filter event, that gets called by the filter-form is filled in.
# set ctx.filter as the string that was sent from the form.
@event('filter')
def filter(ctx, e):
    ctx.filter = e.data['filter']