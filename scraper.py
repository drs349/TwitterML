import httplib2 as http
import json
from datetime import datetime
from datetime import timedelta
from movie_parser import getScoreData
from movie_parser import stringToDate

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json; charset=UTF-8'
}

apikey = 'XET5BXMU7AO6MXCZ3UMQAAAAAA4W66TBZ5JAAAAAAAAFQGYA'
numTweets = '100'
base_url = 'http://otter.topsy.com/search.json'
removed_terms = '-review -reviews -RT -premiere'

method = 'GET'
body = ''
h = http.Http()

def getQuerry(movie_title):
    q_with_spaces = '("' + movie_title + '" OR %23' + movie_title.replace(' ', '') + ') ' + removed_terms
    return q_with_spaces.replace(' ', '%20')

def getMinTime(movie_release_date):
    return getMaxTime(movie_release_date - timedelta(days=3))

def getMaxTime(movie_release_date):
    return movie_release_date.strftime("%s")

def getURL(score_data_element, page):
    mintime = getMinTime(stringToDate(score_data_element[2]))
    maxtime = getMaxTime(stringToDate(score_data_element[2]))
    uri = '?' + 'q=' + getQuerry(score_data_element[0]) + '&mintime=' + mintime + '&maxtime=' + maxtime + '&perpage=' + numTweets + '&type=tweet' + '&allow_lang=en' + '&apikey=' + apikey + '&page=' + str(page)
    return base_url + uri

for element in getScoreData('2013_movie_data.csv')[731:]:
    page = 1
    keepGoing = True
    filename = element[0].replace(' ', '_') + '.txt'
    f = open(filename, "w")
    while keepGoing:
        target = urlparse(getURL(element, page))
        response, content = h.request(target.geturl(), method, body, headers)
        # assume that content is a json reply
        # parse content with the json module
        data = json.loads(content)
        tweet_list = data["response"]["list"]
        for tweet in tweet_list:
            clean_tweet = tweet["content"].encode('ascii', 'ignore')
            #print clean_tweet
            f.write(clean_tweet + '\n')
            f.write('---\n')
        keepGoing = (len(tweet_list) == 100)
        page += 1
    f.close()
    print filename, 'done'
        

