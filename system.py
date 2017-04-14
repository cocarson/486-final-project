# -*- coding: utf-8 -*-

import sys
import ast
import os
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
    print "syllables: " + str(syll)

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

    probabilities = {}
    prev_word = ""

    # print
    #
    # print uniword
    # print biword
    # print syllab_avg

    # for age in uniword:
    #     # print type(age)
    #     # print biword[age]
    #     print str(age) + " : " + str(biword[age].get("I love", 0))

    for tweet in tweets:
        for word in tweet.split(" "):
            for age in uniword:
                if prev_word != "":
                    if age in probabilities:
                        count = float(biword[age].get(prev_word + " " + word, 0))
                        if count > 0:
                            # print str(age) + " : " + str(biword[age].get(prev_word + " " + word, 0)) + " : " + str(log10((float(biword[age].get(prev_word + " " + word, 0) + 1) / 1000))) #(uniword[age].get(prev_word, 0) + max(len(uniword[age]), 1)))))
                            probabilities[age] += log10(count / 100) #(uniword[age].get(prev_word, 0) + max(len(uniword[age]), 1)))
                    else:
                        count = float(biword[age].get(prev_word + " " + word, 0))
                        if count > 0:
                            # print str(age) + " : " + str(biword[age].get(prev_word + " " + word, 0)) + " : " + str(log10((float(biword[age].get(prev_word + " " + word, 0) + 1) / 1000))) #(uniword[age].get(prev_word, 0) + max(len(uniword[age]), 1)))))
                            probabilities[age] = log10(count / 100) #(uniword[age].get(prev_word, 0) + max(len(uniword[age]), 1)))
            prev_word = word

    # print probabilities
    # print max(probabilities)
    # return max(probabilities)

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


def test_system(test_data, uniword, biword, syllab_avg):
    total = 0.0
    correct = 0.0
    within_one = 0.0

    for age in test_data.keys():
        for handle in test_data[age].keys():
            #print test_data[age][handle]
            estimate_age(test_data[age][handle], uniword, biword, syllab_avg)

            # predicted_age = estimate_age(test_data[age][handle], uniword, biword, syllab_avg)

    #         total += 1
    #         if predicted_age == age:
    #             correct += 1
    #         elif predicted_age == (age - 5) or predicted_age == (age + 5):
    #             within_one += 1

    # accuracy = correct / total
    # accuracy_within_one = (correct + within_one) / total

    # print accuracy
    # print accuracy_within_one

# 	vocabs = list()
# 	for i in range(0, len(lang_list)):
# 		count = len(unigrams[i].keys())
# 		vocabs.append(count)

# 	probabilities = [0] * len(lang_list)

# 	prev_char = ''
# 	for char in txt:
# 		both_chars = prev_char + char
# 		if len(both_chars) == 2:
# 			for i in range(0, len(probabilities)):
# 				bigram = bigrams[i]
# 				#print bigram
# 				unigram = unigrams[i]
# 				vocab = vocabs[i]

# 				a = 0
# 				b = 0
# 				if both_chars in bigram:
# 					a = bigram[both_chars]
# 				if prev_char in unigram:
# 					b = unigram[prev_char]

# 				add = float(a + 1) / float(b + vocab)
# 				probabilities[i] += log(add)
# 		prev_char = char

# 	maximum = -1000000.0
# 	index = 0
# 	for i in range(0, len(probabilities)):
# 		#print "prob " + str(i) + " " + str(probabilities[i])
# 		if probabilities[i] > maximum:
# 			maximum = probabilities[i]
# 			index = i

# 	print probabilities
# 	return lang_list[index]

if __name__ == '__main__':

	# #initialize dictionaries with empty dictionaries for each age range
    uniword, biword, syllab_avg = create_dictionaries()

	#loop through tweets in and train system on each tweet
	# for file in os.listdir("tweets/"):
	# 	file = "tweets/" + file
    # obj = {}
    # with open("age_to_tweets") as file:
    #     for line in file.readlines():
    #         obj = ast.literal_eval(line)
		# tweets = []
		# age = 0
		# first_line = True
		# for line in file:
		# 	if first_line:
		# 		age = normalize_age(int(line))
		# 		first_line = False
		# 	else:
		# 		tweets.append(line)

	# train system -> loop over age-tweets dict and train sys
    # for age, tweets in obj.items():
    #     train_system(tweets, int(age), uniword, biword)
    # 	syllab_avg[age] = train_system_syllables(tweets)
    #
	# with codecs.open('saved_dictionaries/uniword', 'w') as output:
	# 	dumped = json.dumps(uniword)
	# 	output.write(dumped)
	# with codecs.open('saved_dictionaries/biword', 'w') as output:
	# 	dumped = json.dumps(biword)
	# 	output.write(dumped)
	# with codecs.open('saved_dictionaries/syllab_avg', 'w') as output:
	# 	dumped = json.dumps(syllab_avg)
	# 	output.write(dumped)

    uniword, biword, syllab_avg = load_dictionaries_from_files()

    # ages = {
    #     20: {
    #         "@covcarson": ["This still happens? 😮", "Calls matter 👏🏼", "This weather is giving me life 🌻👌🏼", "Cutest pupper of all time. #NationalPuppyDay", "Pushing a garbage health care policy through just to say they did is not a victory.", "Apple releasing iOS update with Find My AirPods *and* theater mode for the Apple Watch."]
    #     }
    # }
    #
    # test_system(ages, uniword, biword, syllab_avg)

    while 1:
        username = raw_input("What's your twitter handle?\n")
        demo(username, uniword, biword, syllab_avg)
