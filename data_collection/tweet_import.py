import tweepy
import time
import csv
import json
from config import ckey, csecret, atoken, asecret

print(ckey, csecret, atoken, asecret)
 
# OAuth process, using the keys and tokens
auth = tweepy.OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)

# Creation of the actual interface, using authentication
api = tweepy.API(auth, wait_on_rate_limit=True)

def get_collected():
    already_collected = []
    with open('already_collected.csv') as f:
        readCSV = csv.reader(f, delimiter=',')
        for row in readCSV:
            already_collected.append(row[0])
    return already_collected

def get_trump_supporters():
    trump_supporters = []
    with open('trump_supporters.csv') as f:
        readCSV = csv.reader(f, delimiter=',')
        for row in readCSV:
            trump_supporters.append(row[0])
    return trump_supporters

def get_tweets_list(api, owner, slug, outfile):
    members = []
    already_collected = get_collected()
    for page in tweepy.Cursor(api.list_members, owner, slug).items():
        members.append(page)
    # create a list containing all usernames
    members = [ m.screen_name for m in members[0:200] if m.screen_name not in already_collected]
    print(members)
    for screen_name in members[0:10]:
        account_tweets = tweepy.Cursor(api.user_timeline, screen_name=screen_name).items(750)
        process_tweets(account_tweets, screen_name, outfile)
    return

def process_tweets(account_tweets, screen_name, outfile):
    tweets_list = []
    for status in account_tweets:
        new_tweet = dict()
        new_tweet['account'] = screen_name
        new_tweet['hashtags'] = [hashtag['text'] for hashtag in status._json['entities']['hashtags']]
        new_tweet['urls'] = [url['expanded_url'] for url in status._json['entities']['urls']]
        new_tweet['mentions'] = [user['screen_name'] for user in status._json['entities']['user_mentions']]
        print(new_tweet)
        tweets_list.append(new_tweet)
    with open(outfile, 'a') as fout:
        for tweet in tweets_list:
            fout.write(json.dumps(tweet))
            fout.write('\n')
    with open('already_collected.csv', 'a') as fout:
        writer=csv.writer(fout)
        writer.writerow([screen_name])
    return

def retrieve_followers_from_user(user):
    ''' polls twitter for whom a user is following and returns their screen name and location '''
    screen_names = []
    already_collected = get_collected()
    i = 0
    for user in tweepy.Cursor(api.friends, screen_name=user).items():
        if user.screen_name not in already_collected:
            screen_names.append(user.screen_name)
            i += 1
        if i == 10:
            break 
    return screen_names

def get_supporters_tweet(master_account, party):
    if party == 'Republican':
        outfile = 'tweets_republican_support.txt'
    else:
        outfile = 'tweets_democrat_support.txt'
    screen_names = retrieve_followers_from_user(master_account)
    for screen_name in screen_names:
        account_tweets = tweepy.Cursor(api.user_timeline, screen_name=screen_name).items(750)
        process_tweets(account_tweets, screen_name, outfile)
    return
    

#get_tweets_list(api, 'TheDemocrats', 'house-democrats', 'tweets_democrats_house.txt')
#get_tweets_list(api, 'HouseGOP', 'house-republicans', 'tweets_republicans_house.txt')
get_supporters_tweet('HouseDemocrats', 'Democrats')
get_supporters_tweet('Trump_Support', 'Republicans')


