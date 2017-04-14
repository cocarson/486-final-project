from TwitterAPI import TwitterAPI
from urllib2 import Request, urlopen, URLError
import json
import datefinder
import re
import codecs
from datetime import date

api = TwitterAPI('6hckfkSBDEUJRxPATcCtcsdOp',
            		'GduOLco0wL1pOTboeClVPmZe8PPXEYD0VKnmKWpb2of7UNTbrY',
                    '399687253-xb9c6wdOQMBU8K2Jk3utxDLuqC21qRLTajkV9iel',
                    'bXdT9ejraFk6O9bNExA2sD71jgixMFby8nqzQwfsTLXKa')

#Age range -> list of tweets
age_to_tweet_dict = {}
testing_data = {}

def calculate_age(born):
	today = date.today()
	return today.year - int(born[0]) - ((today.month, today.day) < (int(born[1]), int(born[2])))

def normalize_age(age):
	age /= 5
	age *= 5
	if age < 15:
		age = 15
	if age > 65:
		age = 65

	return age

def get_actor_names(filename):
	with open(filename, 'r') as myfile:
		data = myfile.read()


	names_list = list()
	with open(filename, 'r') as f:
		for line in f:
			if ('(' in line) or ('?' in line):
				continue
			else:
				if is_ascii(line):
					name = line.rstrip('\n')
					name = name.rstrip(' ')
					name = name.split(',')
					if len(name) > 1:
						first_name = name[1][1:]
						last_name = name[0]
						names_list.append(str(first_name) + " " + last_name)

	names_list.append("Mark Ruffalo")
	names_list.append("Channing Tatum")
	return names_list


def get_actor_age(name):
	name = name.replace(' ', '%20')
	try:

		request = Request("http://en.wikipedia.org/w/api.php?action=query&prop=extracts&format=json&exintro=&titles=" + name)

		response = urlopen(request)

		results = response.read()
		TAG_RE = re.compile(r'<[^>]+>')
		request = TAG_RE.sub('', results)
		matches = datefinder.find_dates(request)
	except:
		#print "get_actor_age error"
		return -1
	

	length = 0
	birthdate = ""
	for match in matches:
		if length == 0:
			birthdate = match
		length = length + 1

	if length > 0:
		return birthdate
	else:
		return -1


def is_ascii(s):
	try:
		s.decode('ascii')
		return True
	except UnicodeDecodeError:
		return False

def get_usernames(names):
	usernames = []
	update_names = []
	index  = 0
	for name in names:
		index = index + 1
		if index == 500:
			print name

		try:
			results = api.request('users/search', {'q': name, 'count': 1})
			for item in results:
				if item['verified'] == True:
					update_names.append(name)
					usernames.append(item['screen_name'])
		except:
			#print "get_usernames error"
			continue
	return usernames, update_names

def get_tweets(username, tweets):
	try:
		results = api.request('statuses/user_timeline', {'screen_name': username, 'count': 25, 'include_rts': False})
		for item in results:
			tweets.append(item['text'])
	except:
		#print "get_tweets error"
		return False

	return True

def main():

	names_15 = ["Max Charles", "Zachary Gordon", "Mason Cook", "Nolan Gould", "Millie Bobby Brown", 
	"Caleb McLaughlin", "Gaten Matarazzo", "Noah Schnapp", "Maisie Williams", "Nolan Gould"]
	names_20 = ["Miley Cyrus", "Hailee Steinfeld", "Isabelle Fuhrman", "Kendall Jenner", "Sophie Turner",
	"Demi Lovato", "Keke Palmer", "Debby Ryan", "Selena Gomez", "Asa Butterfield"]
	names_25 = ["Liam Hemsworth", "Zac Efron", "Rihanna", "Grant Gustin", "Colton Haynes", "Nick Jonas",
	"Nicholas Hoult", "Vanessa Hudgens", "Emma Watson", "Lily Collins"]
	names_30 = ["Shay Mitchell", "Robert Pattinson", "Josh Peck", "Usain Bolt", "Lea Michele",
	"Iwan Rheon", "Lucas Grabeel", "Anna Kendrick", "Brittany Snow", "Seth Rogen"]
	names_35 = ["Jodie Sweetin", "Jessica Alba", "Chris Evans", "Kristen Bell", "Channing Tatum",
	"Rebel Wilson", "Chris Pratt", "Jennifer Morrison", "Ian Somerhalder", "Ashton Kutcher"]
	names_40 = ["Ryan Reynolds", "Jessica Chastain", "Reese Witherspoon", "Tobey Maguire",
	"Sarah Paulson", "Leonardo DiCaprio", "Kate Beckinslae", "Seth MacFarlane", "wayne Johnson", "Cameron Diaz"]
	names_45 = ["Mark Wahlberg", "Idina Menzel", "Taraji Henson", "Shemar Moore", "Queen Latifah",
	"Matthew Perry", "Lucy Liu", "Hugh Jackman", "Pamela Anderson", "Pamela Anderson", "Jamie Foxx"]
	names_50 = ["Stephen Colbert", "Steve Carell", "Elizabeth Hurley", "Rainn Wilson",
	"John Stamos", "Michelle Obama", "Robin Wright", "Salma Hayek", "Sarah Jessica Parker", "Robert Downey Jr", "Chris Rock"]
	names_55 = ["Kevin Spacey", "Tim Robbins", "David Duchovny", "Oscar Nunez",
	"Jamie Lee Curtis", "Kathy Griffin", "Ellen DeGeneres", "Barack Obama", "Jim Carrey",
	"George Lopez", "Dan Marino", "John Elway"] 
	names_65 = ["Ben Carson", "Michael Keaton", "Jay Leno", "Jeff Bridges", "Hillary Clinton", "Caitlyn Jenner",
	"Jane Fonda", "Gloria Steinem", "Creed Bratton", "Danny Glover", "Donald Trump"]
	names_60 = ["John Turturro", "Bryan Cranston", "Tom Hanks", "Kris Jenner", "Tim Allen",
	"Dan Aykroyd", "Oprah Winfrey", "Whoopi Goldberg"]

	names = names_15 + names_20 + names_25 + names_30 + names_35 + names_40 + names_45 + names_50 + names_55 + names_60 + names_65

	#names = get_actor_names("aka-names.list")
	tweets = []
	usernames = get_usernames(names)

	counter = 0
	for name, username in zip(usernames[1], usernames[0]):
		print name
		if counter == 500:
			print name

		actor_age = get_actor_age(name)

		if actor_age == -1:
			continue
		actor_age = str(actor_age).split()
		birthdate = actor_age[0]
		birthdate = birthdate.split('-')
		actor_age = calculate_age(birthdate)
		print actor_age

		norm_actor_age = normalize_age(actor_age)

		if get_tweets(username, tweets):
			if (counter % 4) == 0:
				if norm_actor_age in testing_data:
					testing_data[norm_actor_age][name] = tweets
				else:
					testing_data[norm_actor_age] = dict()
					testing_data[norm_actor_age][name] = tweets
			else:
				if norm_actor_age in age_to_tweet_dict:
					age_to_tweet_dict[norm_actor_age] = age_to_tweet_dict[norm_actor_age] + tweets
				else:
					age_to_tweet_dict[norm_actor_age] = tweets
		counter = counter + 1


	#Training Data
	with codecs.open('age_to_tweets', 'w') as output:
		dumped = json.dumps(age_to_tweet_dict)
		output.write(dumped)

	#Test data
	with codecs.open('test_data', 'w') as output:
		dumped = json.dumps(testing_data)
		output.write(dumped)


main()