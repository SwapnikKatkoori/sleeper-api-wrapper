import requests
import json

class BaseApi():
	def _call(self, url):
		result_json_string = requests.get(url);
		result = result_json_string.json()
		return result;