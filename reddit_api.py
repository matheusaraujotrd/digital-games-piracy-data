import praw
import re
from pymongo import MongoClient

def connect_to_mongodb():
    client = MongoClient('mongodb://localhost:27017')
    db = client['jogos_digitais']
    steam_collection = db['steam_appid']
    game_details_collection = db['game_details']
    return steam_collection, game_details_collection

def fetch_game_names(game_details_collection):
    return list(game_details_collection.distinct('Page'))

def compile_regex_patterns(game_names):
    pattern_template = r'(?i)\b{game_name}\b.*'
    return [re.compile(pattern_template.format(game_name=re.escape(game_name))) for game_name in game_names]

def reddit_search(reddit, subreddit, game_names, patterns):
    for game_name, pattern in zip(game_names, patterns):
        for submission in subreddit.search(f"title:{game_name}", sort='new', time_filter='all'):
            if pattern.match(submission.title):
                print(f'Game: {game_name}, Title: {submission.title}, Date: {submission.created_utc}')

def main():
    steam_collection, game_details_collection = connect_to_mongodb()
    
    # Fetch game names from MongoDB
    game_names = fetch_game_names(game_details_collection)

    # Reddit API connection
    reddit = praw.Reddit(
        client_id='pJLTo2TfCwSN3-GypR-vsA',
        client_secret='AI2gxgaoUYbu6BYhWd2MzX0-Xo2qHA',
        user_agent='Jogos Digitais v2.0 by (u/orunemal)',
    )

    # Specify the subreddit
    subreddit_name = 'crackwatch'
    subreddit = reddit.subreddit(subreddit_name)

    # Compile regex patterns
    patterns = compile_regex_patterns(game_names)

    # Perform Reddit API search
    reddit_search(reddit, subreddit, game_names, patterns)

    # Close MongoDB connection
    steam_collection.close()
    game_details_collection.close()

if __name__ == "__main__":
    main()