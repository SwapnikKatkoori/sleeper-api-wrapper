from .base_api import BaseApi

class League(BaseApi):
	def __init__(self, league_id):
		self.league_id = league_id
		self._base_url = "https://api.sleeper.app/v1/league/{}".format(self.league_id)

	def get_league(self):
		return self._call(self._base_url)

	def get_rosters(self):
		return self._call("{}/{}".format(self._base_url,"rosters"))

	def get_users(self):
		return self._call("{}/{}".format(self._base_url,"users"))

	def get_matchups(self, week):
		return self._call("{}/{}/{}".format(self._base_url,"matchups", week))

	def get_playoff_winners_bracket(self):
		return self._call("{}/{}".format(self._base_url,"winners_bracket"))

	def get_playoff_losers_bracket(self):
		return self._call("{}/{}".format(self._base_url,"losers_bracket"))

	def get_transactions(self, week):
		return self._call("{}/{}/{}".format(self._base_url,"transactions", week))

	def get_traded_picks(self):
		return self._call("{}/{}".format(self._base_url,"traded_picks"))

	def get_all_drafts(self):
		return self._call("{}/{}".format(self._base_url, "drafts"))

	def get_standings(self):
		rosters = self.get_rosters()
		users = self.get_users()
		users_dict = {}

		#Maps the user_id to team name for easy lookup
		for user in users:
			try:
				users_dict[user["user_id"]] = user["metadata"]["team_name"]
			except:
				users_dict[user["user_id"]] = user["display_name"]

		roster_standings_list = []
		for roster in rosters:
			wins = roster["settings"]["wins"]
			points = roster["settings"]["fpts"]
			name = roster["owner_id"]
			if name is not None:
				roster_tuple = (wins, points, users_dict[name])
			else:
				roster_tuple = (wins, points, None)
			roster_standings_list.append(roster_tuple)

		roster_standings_list.sort(reverse = 1)

		clean_standings_list = []
		for item in roster_standings_list:
			clean_standings_list.append((item[2], item[0], item[1]))
		
		return clean_standings_list

	def get_highest_scorer(self):
		pass

	def get_lowest_scorer(self):
		pass

	def get_close_games(self, close_num):
		pass

	def empty_roster_spots(self):
		pass