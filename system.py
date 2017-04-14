# -*- coding: utf-8 -*-

import sys
import ast
import os
import pprint
import operator
import re
from math import log10
import codecs
from itertools import izip
from urllib2 import Request, urlopen, URLError
from TwitterAPI import TwitterAPI
import json
from textstat.textstat import textstat
import operator

api = TwitterAPI('6hckfkSBDEUJRxPATcCtcsdOp',
            		'GduOLco0wL1pOTboeClVPmZe8PPXEYD0VKnmKWpb2of7UNTbrY',
                    '399687253-xb9c6wdOQMBU8K2Jk3utxDLuqC21qRLTajkV9iel',
                    'bXdT9ejraFk6O9bNExA2sD71jgixMFby8nqzQwfsTLXKa')

# Age Ranges	: dictionary key
# 	19- 		: 15
# 	20-24		: 20
# 	25-29		: 25
# 	30-34		: 30
# 	35-39		: 35
# 	40-44		: 40
# 	45-59		: 45
# 	50-54		: 50
# 	55-59		: 55
# 	60-64		: 60
# 	65+ 		: 65

def create_dictionaries():
	uniword = {}
	biword = {}
	syllab_avg = {}
	total_tweets = {}

	age = 15
	while age < 70:
		uniword[age] = {}
		biword[age] = {}
		syllab_avg[age] = 0.0
		age += 5

	return uniword, biword, syllab_avg

def normalize_age(age):
	age /= 5
	age *= 5
	if age < 15:
		age = 15
	if age > 65:
		age = 65
	return age

#input: array of all tweets
#input: age of celebrity
#input: uniword dict
#input: biword dict
def train_system(tweets, age, uniword, biword):

    #cycle through tweets and add to uniword and biword dictionaries
    for tweet in tweets:
        prev_word = ""
        for word in tweet.split():
            both_words = str(prev_word + " " + word)
            uniword[age][word] = uniword[age].get(word, 0) + 1

            if prev_word != "":
                biword[age][both_words] = biword[age].get(both_words, 0) + 1
            prev_word = word

        biword[age][word + "\n"] = biword[age].get(word + "\n", 0) + 1

    return

def fetchSyllables(word):
    syll = 1.666666666	#average syll/word in Eng lang.

    syll = textstat.syllable_count(word)

    # request = Request("https://api.datamuse.com/words?sp=" + word + "&md=s")
    # try:
    #     response = urlopen(request)
    #     results = response.read()
    #     dict_format = json.loads(results)
    #     if len(dict_format) > 0:
    #         syll = dict_format[0]["numSyllables"]
    #     print "success"
    #
    # except:
    #     print "exception: " + word

    return syll

def train_system_syllables(tweets):
    syll_count = 0.0
    word_count = 0.0

    # dictionary to remember syllables
    # syllables[word] => num syllables in word
    syllables = {}
    for tweet in tweets:
        syll = 1.666666
        for word in tweet.split():
            if word not in syllables:
                syll = fetchSyllables(word)
            else:
                syll = syllables[word]

            syllables[word] = syll

            word_count += 1.0
            syll_count += syll

    return syll_count/word_count

def load_dictionaries_from_files():
	with open("saved_dictionaries/uniword") as file:
		data = file.read()
	uniword = json.loads(data)
	with open("saved_dictionaries/biword") as file:
		data = file.read()
	biword = json.loads(data)
	with open("saved_dictionaries/syllab_avg") as file:
		data = file.read()
	syllab_avg = json.loads(data)

	return uniword, biword, syllab_avg

def demo(username, uniword, biword, syllab_avg):
	tweets = []

	try:
		results = api.request('statuses/user_timeline', {'screen_name': username, 'count': 200, 'include_rts': False})
		for item in results:
			tweets.append(item['text'])
	except:
		print "You either typed in your username wrong or you don't have a twitter\n"
		return

	if len(tweets) < 1:
		return

	estimate_age(tweets, uniword, biword, syllab_avg)


def estimate_age(tweets, uniword, biword, syllab_avg):
    # print tweets

    probabilities = {}
    prev_word = ""

    for tweet in tweets:
        for word in tweet.split(" "):
            for age in uniword:
                if prev_word != "":
                    if age in probabilities:
                        count = float(biword[age].get(prev_word + " " + word, 0))
                        if count > 0:
                            probabilities[age] += log10(count / 100) #(uniword[age].get(prev_word, 0) + max(len(uniword[age]), 1)))
                    else:
                        count = float(biword[age].get(prev_word + " " + word, 0))
                        if count > 0:
                            probabilities[age] = log10(count / 100) #(uniword[age].get(prev_word, 0) + max(len(uniword[age]), 1)))
            prev_word = word

    probs_sorted = sorted(probabilities.items(), key=operator.itemgetter(1), reverse = True)
    count = 1
    print "Your predicted age based on your tweets is:"

    for age_prob in probs_sorted:
        if count > 3:
            break
        age = int(age_prob[0])
        max_age = age + 4
        print str(count) + ") " + str(age) + " - " + str(max_age)
        count += 1

    return probs_sorted[0][0]


def test_system(test_data, uniword, biword, syllab_avg):
    total = 0.0
    correct = 0.0
    within_one = 0.0

    for age in test_data.keys():
        for handle in test_data[age].keys():
            predicted_age = int(estimate_age(test_data[age][handle], uniword, biword, syllab_avg))

            total += 1
            if predicted_age == int(age):
                correct += 1
            elif predicted_age == (int(age) - 5) or predicted_age == (int(age) + 5):
                within_one += 1

            print "(" + str(int(correct)) + "/" + str(int(total)) + ")"

    accuracy = correct / total
    accuracy_within_one = (correct + within_one) / total

    print "Accuracy: " + str(accuracy)
    print "Within one: " + str(accuracy_within_one)

def read_and_train(uniword, biword, syllab_avg):
    # loop through tweets in and train system on each tweet
    for file in os.listdir("tweets/"):
        file = "tweets/" + file
        obj = {}
        with open("age_to_tweets") as file:
            for line in file.readlines():
                obj = ast.literal_eval(line)


    # train system -> loop over age-tweets dict and train sys
    for age, tweets in obj.items():
        train_system(tweets, int(age), uniword, biword)
        average = train_system_syllables(tweets)
        syllab_avg[age] = average
    
    with codecs.open('saved_dictionaries/uniword', 'w') as output:
        dumped = json.dumps(uniword)
        output.write(dumped)
    with codecs.open('saved_dictionaries/biword', 'w') as output:
        dumped = json.dumps(biword)
        output.write(dumped)
    with codecs.open('saved_dictionaries/syllab_avg', 'w') as output:
        dumped = json.dumps(syllab_avg)
        output.write(dumped)

def run_system(uniword, biword, syllab_avg):
    while 1:
        username = raw_input("What's your twitter handle?\n")
        demo(username, uniword, biword, syllab_avg)

if __name__ == '__main__':

	# #initialize dictionaries with empty dictionaries for each age range
    uniword, biword, syllab_avg = create_dictionaries()

    # only needed to fill the file - comment out otherwise
    # print "training..."
    # read_and_train(uniword, biword, syllab_avg)

    uniword, biword, syllab_avg = load_dictionaries_from_files()

    # if running or testing
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        with open("test_data") as file:
            for line in file.readlines():
                ages = ast.literal_eval(line)
        test_system(ages, uniword, biword, syllab_avg)
    else:
        run_system(uniword, biword, syllab_avg)



# old code
        # tweets = []
        # age = 0
        # first_line = True
        # for line in file:
        #   if first_line:
        #       age = normalize_age(int(line))
        #       first_line = False
        #   else:
        #       tweets.append(line)