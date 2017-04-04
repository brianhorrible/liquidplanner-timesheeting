#/usr/bin/python

import os
import requests
import json

#The following getenv only works in Unix environments and thus this script does not currently support Windows.
authentication_token_location = (os.getenv('HOME')+'/.lp-time/auth-token')

def check_if_auth_token_directory_exists():
	try:
		os.makedirs(os.path.dirname(authentication_token_location))
	except OSError:
		pass

def check_authentication_token():
	check_if_auth_token_directory_exists()
	try:
		authentication_token = (open(authentication_token_location,'r')).read().strip()
		return authentication_token
	except Exception:
		print('Authentication token does not exist. Please go to Liquidplanner >> Settings >> My API Tokens and generate a key.')
		auth_input = raw_input('Please enter a valid API key now. We will automatically save this token for future use.\n')
		authentication_token = save_new_authentication_token(auth_input)
		return authentication_token

def save_new_authentication_token(auth_input):
	with open(authentication_token_location,'w') as f:
		save_token = f.write(auth_input)
	return auth_input

class LiquidPlanner:
	lp_url = 'https://app.liquidplanner.com/api'
	authentication_token=None

	def __init__(self, authentication_token):
		self.authentication_token = authentication_token

	def validate_authentication_token(self):
		if (self.get('/account').status_code == 200):
			pass
		else:
			raise Exception("\n\nInvalid API key was passed in or LiquidPlanner is down. Please double check keys in " + authentication_token_location)

	def get(self, uri, options={}):
		return requests.get(self.lp_url + uri, 
		data=options,
		headers={'Authorization': 'Bearer ' + self.authentication_token, 
		'Content-Type': 'application/json'}
		)			

	def post(self, uri, options={}):
		return requests.post(self.lp_url + uri,
		data=options,
		headers={'Authorization': 'Bearer ' + self.authentication_token,
		'Content-Type': 'application/json'}
		)

	def put(self, uri, options={}):
		return requests.put(self.lp_url + uri,
		data=options,
		headers={'Authorization': 'Bearer ' + self.authentication_token,
		'Content-Type': 'application/json'}
		)

