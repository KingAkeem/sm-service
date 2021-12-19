from flask import json, Flask, request, abort 
from flask_cors import CORS
from markupsafe import escape

from lib.twitter import InvalidAddressError, read_tweet_arguments, scrape_tweets, scrape_user

"""
Current requirements:
- flask
- geopy
- twint
"""

app = Flask(__name__)
CORS(app)

@app.route("/search/tweets")
def get_tweets():
	tweet_args = read_tweet_arguments(request.args)
	try:
		features, origin = scrape_tweets(tweet_args)
		print(features, origin)
		return json.jsonify({'features': features, 'origin': origin})
	except InvalidAddressError:
		abort(400)


@app.route("/search/user")
def get_user():
	username = escape(request.args.get('username', '', type=str))
	users = scrape_user(username=username)
	return json.jsonify(users)