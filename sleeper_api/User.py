class User():
	def __init__(self, user_id):
		self.user_id = user_id
		self._base_url = "https://api.sleeper.app/v1/user/{}".format(self.user_id)

	def get_user(self):
		return self._call(self._base_url)

	def get_all_leagues(self, season):
		
		return self._call("{}/{}/nfl/{}".format(self._base_url, "leagues", season))

	def get_all_drafts(self):
		pass