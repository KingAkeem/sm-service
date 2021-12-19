from geojson import Feature
from twint import run, Config
from geopy.geocoders import Nominatim

batch_size = 20 # twint uses increments of 20
TWEET_LIMIT = 1 * batch_size 
DEFAULT_DISTANCE = 1 # Miles


class InvalidAddressError(Exception):
	def __init__(self, address, message='Address is not properly formatted.'):
		self.address = address
		self.message = message
		super().__init__(self.message)	

	def __str__(self):
		return f'{self.address} -> {self.message}'

def read_tweet_arguments(args):
	return {
		'user': args.get('user', None, type=str),
		'limit': args.get('limit', TWEET_LIMIT, type=int),
		'keyword': args.get('keyword', None, type=str),
		'city': args.get('city', None, type=str),
		'distance_in_miles': args.get('distance', DEFAULT_DISTANCE, type=int),
	}

def format_location(address, distance):
	if not address:
		return None
	
	#https://geopy.readthedocs.io/en/stable/#nominatim
	geolocator = Nominatim(user_agent='twitter-service')
	try: 
		coordinate = geolocator.geocode(address)
		return f"{coordinate.latitude},{coordinate.longitude},{distance}mi", coordinate
	except AttributeError:
		raise InvalidAddressError(address)

def to_features(tweets):
	features = []
	for tweet in tweets:
		if tweet.place: # place corresponds to a point geometry
			features.append(Feature(geometry=tweet.place, properties=vars(tweet)))
	return features

def scrape_tweets(args):
	tweets = []
	c = Config(
		Limit=int(args['limit']),
		Store_object=True,
		Store_object_tweets_list=tweets,
		Hide_output=True,
	)

	# validate city and distance in miles
	# add formats that city can be in based on geopy
	# distance should be a number (integer/float) that is greater than 0.
	if args['city']:
		c.Geo, coordinate = format_location(args['city'], args['distance_in_miles'])

	if args['keyword'] != 'None':
		c.Search = args['keyword']
	
	if args['user']:
		c.Username = args['user']

	run.Search(c) # run config once filters have been added
	return to_features(tweets), { 'latitude': coordinate.latitude, 'longitude': coordinate.longitude } 

def scrape_user(username):
	users = []
	run.Lookup(Config(
		Username=username,
		Store_object=True,
		Hide_output=True,
		Store_object_users_list=users
	))
	return vars(user=users.pop())