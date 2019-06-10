from .base_api import BaseApi

class User(BaseApi):
	def __init__(self, initial_user_input):
		self.user_id = ""
		self._base_url = "https://api.sleeper.app/v1/user"
		self._user = self._call("{}/{}".format(self._base_url,initial_user_input))
		self.username = self._user["username"]
		self.user_id = self._user["user_id"]

	def get_user(self):
		return self._user

	def get_all_leagues(self, sport, season):
		return self._call("{}/{}/{}/{}/{}".format(self._base_url, self.user_id, "leagues", sport, season))

	def get_all_drafts(self, sport, season):
		return self._call("{}/{}/{}/{}/{}".format(self._base_url, self.user_id, "drafts",sport, season ))