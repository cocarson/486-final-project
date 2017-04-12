from TwitterAPI import TwitterAPI

api = TwitterAPI('6hckfkSBDEUJRxPATcCtcsdOp',
            		'GduOLco0wL1pOTboeClVPmZe8PPXEYD0VKnmKWpb2of7UNTbrY',
                    '399687253-xb9c6wdOQMBU8K2Jk3utxDLuqC21qRLTajkV9iel',
                    'bXdT9ejraFk6O9bNExA2sD71jgixMFby8nqzQwfsTLXKa')

def get_usernames(names):
	usernames = []

	for name in names:
		results = api.request('users/search', {'q': name, 'count': 1})
		for item in results:
			if item['verified'] == True:
				usernames.append(item['screen_name'])
	return usernames

def get_tweets(username, tweets):
	tweet_list = []
	results = api.request('statuses/user_timeline', {'screen_name': username, 'count': 40, 'include_rts': False})
	for item in results:
		tweet_list.append(item['text'])

	tweets[username] = tweet_list

def main():
	names = ["Steve Carell", "Steve Martin", "Idris Elba"]
	tweets = {}
	usernames = get_usernames(names)
	for username in usernames:
		get_tweets(username, tweets)

	for key in tweets:
		print key
		print tweets[key]
		print "\n"


main()