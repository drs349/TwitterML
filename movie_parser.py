from datetime import datetime
from random import shuffle
from math import sqrt
from collections import defaultdict
import os

def stringToDate(date):
    parts = date.split(' ')
    day = None
    month = None
    if (len(parts)==3):
        if (parts[0] == 'Jan'):
            month = 1
        elif (parts[0] == 'Feb'):
            month = 2
        elif (parts[0] == 'Mar'):
            month = 3
        elif (parts[0] == 'Apr'):
            month = 4
        elif (parts[0] == 'May'):
           month = 5
        elif (parts[0] == 'Jun'):
            month = 6
        elif (parts[0] == 'Jul'):
            month = 7
        elif (parts[0] == 'Aug'):
            month = 8
        elif (parts[0] == 'Sep'):
            month = 9
        elif (parts[0] == 'Oct'):
            month = 10
        elif (parts[0] == 'Nov'):
            month = 11
        elif (parts[0] == 'Dec'):
            month = 12
        day = int(parts[1].split(',')[0])
    else:
        parts = date.split('/')
        day = int(parts[0])
        month = int(parts[1])
    year = int(parts[2])
    return datetime(year, month, day)

def parse_tweets(filename):
    file = open(filename, 'r')
    fullstring = file.read()
    fullstring = fullstring.replace("http://t.co/", "CS4780_PROJECT_LINK_TOKEN")
    #fullstring = fullstring.replace("#", "CS4780_PROJECT_HASHTAG_TOKEN") 
    fullstring = fullstring.replace("'", "")
    fullstring = fullstring.replace(".", " ")
    fullstring = fullstring.replace("(", " ")
    fullstring = fullstring.replace(")", " ")
    fullstring = fullstring.replace(":", " ")
    fullstring = fullstring.replace(";", " ")
    fullstring = fullstring.replace(",", " ")
    fullstring = fullstring.replace("\n", "")
    fullstring = fullstring.replace('"', "")
    fullstring = fullstring.replace("---", " ")
    fullstring = fullstring.replace("&amp", " and ")
    d = defaultdict(float)
    tweetData = fullstring.split(" ")
    for word in tweetData:
        if word != "":
            if word.find("CS4780_PROJECT_LINK_TOKEN") >= 0:
                d["CS4780_PROJECT_LINK_TOKEN"] += 1
            #elif word.find("CS4780_PROJECT_HASHTAG_TOKEN") >= 0:
            #    d["CS4780_PROJECT_HASHTAG_TOKEN"] += 1
            else:
                d[word.lower()] += 1
    totalwords = 0.0
    for value in d.itervalues():
        totalwords += value
    if totalwords == 0:
        print filename
    for key in d.iterkeys():
        d[key] /= totalwords
    return d

def L2_norm(first, second):
    s = 0.0
    for k, v in first.iteritems():
        s += (v - second[k]) ** 2
    for k, v in second.iteritems():
        if not k in first:
            s += v ** 2
    return sqrt(s)

def L1_norm(first, second):
    s = 0.0
    for k, v in first.iteritems():
        s += abs(v - second[k])
    for k, v in second.iteritems():
        if not k in first:
            s += abs(v)
    return s

def LN_norm(first, second, n):
    # this function is untested
    s = 0.0
    for k, v in first.iteritems():
        s += abs(v - second[k]) ** n
    for k, v in second.iteritems():
        if not k in first:
            s += abs(v) ** n
    return s ** (1 / float(n))

def scoreCalc(point):
    return float(point[0])

def runKNN(point, trainingData, k=5, norm=L2_norm):
    relData = sorted(trainingData, key=lambda x: norm(point[1], x[1]))[:k]
    distances = map(lambda x: norm(point[1], x[1]), relData)
    scores = map(scoreCalc, relData)

    totalDistance = sum(distances)
    if totalDistance == 0:
        print distances

    score = 0
    for i in range(len(distances)):
        score += distances[i] / float(totalDistance) * scores[i]

    return score

def runKNN_all(point, trainingData, max_k, true_value, norm=L2_norm):
    relData = sorted(trainingData, key=lambda x: norm(point[1], x[1]))
    distances = map(lambda x: norm(point[1], x[1]), relData)
    scores = map(scoreCalc, relData)

    errors = []
    for k in range(1, max_k):
        totalDistance = sum(distances[:k])
        if totalDistance == 0:
            totalDistance = 1
            print 'div by zero error avoided naively'
        score = 0
        for i in range(k):
            score += distances[i] / float(totalDistance) * scores[i]
        errors.append(abs(score - true_value))
    return errors

def log_output(str):
    f = open('results.txt', 'a')
    f.write(str + '\n')
    print str


score_data_file = open('2012_movie_data.csv', 'r')
score_data_lines = []
for line in score_data_file:
    line = line.rstrip()
    line = line.replace('"', '')
    line = line.replace(':', '')
    line = line.replace('-', '')
    line = line.replace("'", '')
    score_data_lines.append(line)
score_data = zip(score_data_lines[0::3], score_data_lines[1::3], score_data_lines[2::3])

shuffle(score_data)

average_score_sum = 0.0
for score in score_data:
    average_score_sum += float(score[1])
average_score = average_score_sum / len(score_data)
print 'average score is', average_score

guess_average_error_sum = 0.0
for score in score_data:
    guess_average_error_sum += abs(average_score - float(score[1]))
guess_average_error = guess_average_error_sum / len(score_data)
print 'error from guessing the average is', guess_average_error

for guess in range(55, 60):
    guess_error_sum = 0.0
    for score in score_data:
        guess_error_sum += abs(guess - float(score[1]))
    guess_error = guess_error_sum / len(score_data)
    print 'error from guessing', guess, 'is', guess_error

split_value = len(score_data)/5

training_data = score_data[split_value:]
validation_data = score_data[:split_value]
log_output('training movies: ' + str(len(training_data)))
log_output('validation movies: ' + str(len(validation_data)))

training_tweets_raw = []
validation_tweets = []

documentFreq = defaultdict(float)

for movie in training_data:
    filename = movie[0].replace(' ', '_') + '.txt'
    parsed = parse_tweets(filename)
    training_tweets_raw.append((movie[1], parsed))
    for k, v in parsed.iteritems():
        documentFreq[k] += 1.0 / len(training_data)

training_tweets = []
for movie, raw_dict in training_tweets_raw:
    upd_dict = defaultdict(float)
    for k, v in raw_dict.iteritems():
        upd_dict[k] = raw_dict[k] / documentFreq[k]
    training_tweets.append((movie, upd_dict))
    
for movie in validation_data:
    filename = movie[0].replace(' ', '_') + '.txt'
    raw_dict = parse_tweets(filename)
    upd_dict = defaultdict(float)
    for k, v in raw_dict.iteritems():
        upd_dict[k] = raw_dict[k] / documentFreq[k] if documentFreq[k] != 0 else 0
    validation_tweets.append((movie[1], upd_dict))

def exportSVMLightData(tweets, map_so_far, filename):
    light_data = ''

    next_val = len(map_so_far) + 1
    for movie in tweets:
        light_data += str(scoreCalc(movie))
        light_map = defaultdict(float)
        for k, v in movie[1].iteritems():
            if map_so_far[k] == 0:
                map_so_far[k] = next_val
                next_val += 1
            light_map[map_so_far[k]] = v 

        # Sort the indices
        for k, v in zip(sorted(light_map), [light_map[i] for i in sorted(light_map)]):
            light_data += ' ' + str(k) + ':' + str(v)
        light_data += '\n'

    svmfile = open(filename, 'w')
    svmfile.write(light_data)
    svmfile.close()

exportSVMLightData(training_tweets, defaultdict(int), "tweets.train")
exportSVMLightData(validation_tweets, defaultdict(int), "tweets.val")

os.system("./svm_learn -z r tweets.train model")
os.system("./svm_classify tweets.val model predictions")

max_k = len(training_tweets)

errors = [0.0 for i in range(1, max_k)]
count = 0
for movie in validation_tweets:
    count += 1
    print count, 'movies done of', len(validation_tweets)
    temp_errors = runKNN_all(movie, training_tweets, max_k, scoreCalc(movie), L1_norm)
    for k in range(1, max_k):
        errors[k-1] += temp_errors[k-1]/float(len(validation_tweets))
        
min_error = 100.0
k_of_min_error = 0
for k in range(1, max_k):
    if errors[k-1] < min_error:
        min_error = errors[k-1]
        k_of_min_error = k
    print str(k) + ' yields average error ' + str(errors[k-1])
log_output(str(k_of_min_error) + ' achieved the minimum error, which was ' + str(min_error))
