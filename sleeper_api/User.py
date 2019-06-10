class User():
	def __init__(self, user_id):
		self.user_id = user_id

	def get_all_leagues(self, season):
		base_url = "https://api.sleeper.app/v1/user/{}/leagues/nfl/{}".format(self.user_id, season)
		return self.call(base_url)

	def get_all_drafts(self):
		pass

	def get