from sleeper_api import BaseApi

class Stats(BaseApi):
	def __init__(self):
		self._base_url = "https://api.sleeper.app/v1/stats/{}".format("nfl")
		self._projections_base_url = "https://api.sleeper.app/v1/projections/{}".format("nfl")
		self._full_stats = None

	def get_all_stats(self, season_type, season):
		return self._call("{}/{}/{}".format(self._base_url, season_type, season)) 
		#Temporary caching of full stats

	def get_week_stats(self, season_type, season, week):
		return self._call("{}/{}/{}/{}".format(self._base_url, season_type, season, week))

	def get_all_projections(self, season_type, season):
		return self._call("{}/{}/{}".format(self._projections_base_url, season_type, season))

	def get_week_projections(self, season_type, season, week):
		return self._call("{}/{}/{}/{}".format(self._projections_base_url, season_type, season, week))

	def get_player_score(self, player_id, season, week):
		result_dict = {}
		stats = self.get_week_stats("regular", season, week)
		try:
			player_stats = stats[player_id]
		except:
			raise Exception("player_id not found")

		if stats:
			print(player_stats)
			try:
				result_dict["pts_ppr"] = player_stats["pts_ppr"]
			except:
				result_dict["pts_ppr"] = "Not Available"

			try:
				result_dict["pts_std"] = player_stats["pts_std"]
			except:
				result_dict["pts_std"] = "Not Available"

			try:
				result_dict["pts_half_ppr"] = player_stats["pts_half_ppr"]
			except:
				result_dict["pts_half_ppr"] = "Not Available"

		return result_dict
		