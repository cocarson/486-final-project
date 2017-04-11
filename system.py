import sys
import os
import re
from math import log
import codecs
from itertools import izip

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

	age = 15
	while age < 70:
		uniword[age] = {}
		biword[age] = {}
		age += 5

	return uniword, biword

#input: array of all tweets
#input: age of celebrity
#input: uniword dict
#input: biword dict
def train_system(tweets, age, uniword, biword):
	#normalize age
	age /= 5
	age *= 5
	if age < 15:
		age = 15
	if age > 65:
		age = 65

	#cycle through tweets and add to uniword and biword dictionaries
	for tweet in tweets:
		prev_word = ""
		for word in tweet.split():
			both_words = prev_word + " " + word
			uniword[age][word] = uniword[age].get(word, 0) + 1

			if prev_word != "":
				biword[age][both_words] = biword[age].get(both_words, 0) + 1
			prev_word = word

		biword[age][word + "\n"] = biword[age].get(word + "\n", 0) + 1

	return

# def estimate_age(tweets, uniword, biword):
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

	#initialize dictionaries with empty dictionaries for each age range
	uniword, biword = create_dictionaries()

	#loop through tweets in and train system on each tweet
	for file in os.listdir("tweets/"):
		file = "tweets/" + file
		with open(file) as file:
			tweets = []
			age = 0
			first_line = True
			for line in file:
				if first_line:
					age = int(line)
					first_line = False
				else:
					tweets.append(line)

		#train system 
		train_system(tweets, age, uniword, biword)
	

	print uniword
	print "\n"
	print biword



	# test = str(sys.argv[1])
	# i = 0
	# with codecs.open('languageIdentification.output', 'w') as output:
	# 	with codecs.open(test, 'r') as file:
	# 		for line in file:
	# 			output.write(str(i + 1) + " " + identifyLanguage(line, langs, unigrams, bigrams) + "\n")
	# 			i += 1


