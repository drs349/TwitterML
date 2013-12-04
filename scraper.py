import httplib2 as http
import json
from datetime import datetime
from datetime import timedelta
import movie_parser as parser

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json; charset=UTF-8'
}

apikey = 'SMQWWQFZBRDZTIXJMUMQAAAAABNQ6RLLSVJAAAAAAAAFQGYA'
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

def getURL(score_data_element):
    mintime = getMinTime(parser.stringToDate(score_data_element[2]))
    maxtime = getMaxTime(parser.stringToDate(score_data_element[2]))
    uri = '?' + 'q=' + getQuerry(score_data_element[0]) + '&mintime=' + mintime + '&maxtime=' + maxtime + '&perpage=' + numTweets + '&type=tweet' + '&allow_lang=en' + '&apikey=' + apikey
    return base_url + uri

for element in parser.score_data[0:]:
    target = urlparse(getURL(element))
    response, content = h.request(target.geturl(), method, body, headers)
    # assume that content is a json reply
    # parse content with the json module
    data = json.loads(content)
    tweet_list = data["response"]["list"]
    filename = element[0].replace(' ', '_') + '.txt'
    f = open(filename, "w")
    for tweet in tweet_list:
        clean_tweet = tweet["content"].encode('ascii', 'ignore')
        #print clean_tweet
        f.write(clean_tweet + '\n')
        f.write('---\n')
    print filename, 'done'
        

