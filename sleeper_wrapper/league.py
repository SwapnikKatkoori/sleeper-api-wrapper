from .base_api import BaseApi

class League(BaseApi):
	def __init__(self, league_id):
		self.league_id = league_id
		self._base_url = "https://api.sleeper.app/v1/league/{}".format(self.league_id)
		self._league = self._call(self._base_url)

	def get_league(self):
		return self._league

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

	def map_users_to_team_name(self, users):
		""" returns dict {user_id:team_name}"""
		users_dict = {}

		#Maps the user_id to team name for easy lookup
		for user in users:
			try:
				users_dict[user["user_id"]] = user["metadata"]["team_name"]
			except:
				users_dict[user["user_id"]] = user["display_name"]
		return users_dict

	def get_standings(self, rosters, users):
		users_dict = self.map_users_to_team_name(users)

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
			clean_standings_list.append((item[2], str(item[0]), str(item[1])))
		
		return clean_standings_list

	def map_rosterid_to_ownerid(self, rosters ):
		"""returns: dict {roster_id:[owner_id,pts]} """
		result_dict = {}
		for roster in rosters:
			roster_id = roster["roster_id"]
			owner_id = roster["owner_id"]
			result_dict[roster_id] = owner_id

		return result_dict

	def get_scoreboards(self, rosters, matchups, users):
		""" returns dict {matchup_id:[(team_name,score), (team_name, score)]}"""
		roster_id_dict = self.map_rosterid_to_ownerid(rosters)

		
		if len(matchups) == 0:
			return None

		#Get the users to team name stats
		users_dict = self.map_users_to_team_name(users)


		#map roster_id to points 
		scoreboards_dict = {}

		for team in matchups:
			matchup_id = team["matchup_id"]
			current_roster_id = team["roster_id"]
			owner_id = roster_id_dict[current_roster_id]
			if owner_id is not None:
				team_name = users_dict[owner_id]
			else:
				team_name = "Team name not available"
			team_score = team["points"]
			team_score_tuple = (team_name, team_score)

			if matchup_id not in scoreboards_dict:
				scoreboards_dict[matchup_id] = [team_score_tuple]
			else:
				scoreboards_dict[matchup_id].append(team_score_tuple)
		return scoreboards_dict

	def get_close_games(self, scoreboards, close_num):
		""" -Notes: Need to find a better way to compare scores rather than abs value of the difference of floats. """
		close_games_dict = {}
		for key in scoreboards:
			team_one_score = scoreboards[key][0][1]
			team_two_score = scoreboards[key][1][1]

			if abs(team_one_score-team_two_score) < close_num:
				close_games_dict[key] = scoreboards[key]
		return close_games_dict

	def empty_roster_spots(self):
		pass

	def get_negative_scores(self, week):
		pass

	def get_rosters_players(self):
		pass
