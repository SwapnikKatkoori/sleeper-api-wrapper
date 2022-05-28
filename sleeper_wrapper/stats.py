import pdb
from sleeper_wrapper.base_api import BaseApi
from sleeper_wrapper.players import Players
import json
from pathlib import Path
import pandas as pd
from operator import itemgetter, attrgetter, getitem
SCORING_TYPES = ["ppr", "std", "custom"]


class Stats(BaseApi):
    def __init__(self, season=2021, season_type="regular", position_list=["QB", "RB", "WR", "TE", "DEF", "K"], **kwargs):
        self.season = season
        self.season_type = season_type
        self.position_list = position_list
        self.vbd_baseline_ranks = {'RB': 24, 'QB': 24, 'WR': 36, 'TE': 12, 'K': 12, 'DEF': 12}
        self.vbd_baseline_scores = {}
        self.scoring_settings = kwargs.get("scoring_settings")
        self.week_start = kwargs.get("week_start")
        self.week_stop = kwargs.get("week_stop")
        self.stats_list = []
        self.week_stats_list = []
        self.totals_dict = {}
        self.average_dict = {}
        self._base_url = "https://api.sleeper.app/v1/stats/{}".format("nfl")
        self._projections_base_url = "https://api.sleeper.app/v1/projections/{}".format("nfl")
        self._full_stats = None
        self.stats = self.get_stats()
        self.df = pd.DataFrame(self.stats_list)

    def get_stats(self) -> object:
        if self.week_start:
            self.check_week_range()
            return self.get_week_stats()
        else:
            return self.get_year_stats()

    def get_year_stats(self):
        dir_path = Path(f'data/stats/{self.season}')
        file_path = Path(f'data/stats/{self.season}/all_stats_{self.season}.json')
        try:
            with open(file_path, "r") as data_file:
                self.stats = json.load(data_file)
        except FileNotFoundError:
            dir_path.mkdir(parents=True, exist_ok=True)
            self.stats = self._call(f"{self._base_url}/{self.season_type}/{self.season}")
            self.map_player_info()
            with open(file_path, 'w') as data_file:
                json.dump(self.stats, data_file, indent=4)
        finally:
            self.trim_to_positions()
            self.make_stats_list()
            if self.scoring_settings:
                self.get_custom_score()
                self.add_rank_custom("custom")
                self.add_pos_rank_custom("custom")
            self.get_vbd_baseline_players()
            self.calc_vbd_score()
        return self.stats

    def get_week_stats(self):
        for week in range(self.week_start, self.week_stop+1):
            dir_path = Path(f'data/stats/{self.season}')
            file_path = Path(f'data/stats/{self.season}/week_{week:02d}_stats_{self.season}.json')
            try:
                with open(file_path, "r") as json_file:
                    self.stats = json.load(json_file)
            except FileNotFoundError:
                print("local path and file not found, making API call")
                dir_path.mkdir(parents=True, exist_ok=True)
                self.stats = self._call(f"{self._base_url}/{self.season_type}/{self.season}/{week}")
                self.map_player_info()
                with open(file_path, 'w') as data_file:
                    json.dump(self.stats, data_file, indent=4)
            finally:
                self.trim_to_positions()
                self.fix_empty_scores()
                self.make_stats_list()
                self.week_stats_list.append(self.stats)
                if self.scoring_settings:
                    self.get_custom_score()
                self.add_rank_custom()
                self.add_pos_rank_custom()
                self.get_vbd_baseline_players()
                self.calc_vbd_score()

        self.get_stats_totals()
        self.get_stats_average()
        # pdb.set_trace()
        # self.stats = self.get_stats_totals()
        # self.stats = self.get_stats_average()
        return self.stats

    def get_stats_average(self):
        exclude_keys = ["position", "name", "age", "sleeper_id", "total_gp", "total_gms_active",
                        "total_pts_ppr", "total_pts_custom", "total_pts_std"]
        self.average_dict = self.totals_dict

        for p in self.average_dict:
            if "gp" in self.average_dict[p].keys():
                games_played = self.average_dict[p]["gp"]
                for k, v in self.average_dict[p].items():
                    if type(v) == str or k in exclude_keys:
                        pass
                    else:
                        self.average_dict[p][k] = round(v / games_played, 2)
            else:
                pass

        return self.average_dict

    def get_stats_totals(self):
        # TODO: work on keys to exclude from totalling
        # take sorted stats list and add all columns
        # goal is to return single dict ordered by column choice
        totals_dict = {}
        exclude_keys = ["position", "name", "age", "sleeper_id"]
        for week in self.week_stats_list:
            for player, stats in week.items():
                if player not in totals_dict:
                    totals_dict[player] = week[player]
                else:
                    for k, v in week[player].items():
                        if k not in exclude_keys:
                            try:
                                totals_dict[player][k] += round(v, 2)
                            except KeyError:
                                totals_dict[player][k] = round(v, 2)
        # pdb.set_trace()
        for p in totals_dict:
            totals_dict[p]['total_gp'] = totals_dict[p]['gp']
            totals_dict[p]["total_gms_active"] = totals_dict[p]['gms_active']
            totals_dict[p]["total_pts_ppr"] = totals_dict[p]['pts_ppr']
            totals_dict[p]["total_pts_custom"] = totals_dict[p]['pts_custom']
            totals_dict[p]["total_pts_std"] = totals_dict[p]['pts_std']

        self.totals_dict = totals_dict
        # self.make_stats_list()
        return self.totals_dict

    def check_week_range(self):
        if not self.week_stop or self.week_stop < self.week_start:
            self.week_stop = self.week_start

    def trim_to_positions(self):
        self.stats = {
            k: v for k, v in self.stats.items()
            if self.stats[k]["position"] in self.position_list and "gp" in self.stats[k].keys()
        }

    def add_pos_rank_custom(self):
        for scoring_type in SCORING_TYPES:
            self.stats_list = sorted(self.stats_list, key=lambda i: i[f"pts_{scoring_type}"], reverse=True)
            self.stats_list = sorted(self.stats_list, key=lambda i: i[f"position"], reverse=True)
            pos_rank_counter = 1  # this will reset for each position
            for player in self.stats_list:
                index = self.stats_list.index(player)
                player[f"pos_rank_{scoring_type}"] = pos_rank_counter
                if index == 0:  # skips the first item, where index -1 would be the last item of the list
                    pos_rank_counter += 1
                else:
                    if self.stats_list[index]["position"] == self.stats_list[index - 1]["position"]:
                        pos_rank_counter += 1
                    else:
                        pos_rank_counter = 1
        # print(self.stats_list)
        # pdb.set_trace()

    def add_rank_custom(self):
        #  loop through positions because weekly stats don't have the position or overall rankings like the yearly stats
        for scoring_type in SCORING_TYPES:
            self.stats_list = sorted(self.stats_list, key=lambda i: i[f"pts_{scoring_type}"], reverse=True)
            rank_counter = 1  # this will be the total overall rank for the scoring of all players in the position_list
            for player in self.stats_list:
                player[f"rank_{scoring_type}"] = rank_counter
                rank_counter += 1

    def get_vbd_baseline_players(self):
        # compare player's score with X score at that position
        # get baselines
        for scoring_type in SCORING_TYPES:
            v_dict = self.vbd_baseline_ranks
            for p in self.stats_list:
                position = p["position"]
                pos_rank_custom = p[f"pos_rank_{scoring_type}"]
                if v_dict[position] == pos_rank_custom:
                    self.vbd_baseline_scores[position] = p[f"pts_{scoring_type}"]
                else:
                    pass

    def calc_vbd_score(self):
        for scoring_type in SCORING_TYPES:
            v_ranks = self.vbd_baseline_ranks
            v_scores = self.vbd_baseline_scores
            for p in self.stats_list:
                position = p["position"]
                pos_rank = p[f"pos_rank_{scoring_type}"]
                # pdb.set_trace()
                if v_ranks[position] > pos_rank:
                    p[f"vbd_{scoring_type}"] = p[f"pts_{scoring_type}"] - v_scores[position]
                else:
                    p[f"vbd_{scoring_type}"] = 0.0

    def map_player_info(self):
        # Adds player name, age and position to stats_dict json for saving
        players = Players()
        for player in self.stats:
            self.stats[player]['sleeper_id'] = player
            try:
                self.stats[player]['position'] = players.all_players[player]['position']
            except KeyError:
                self.stats[player]['position'] = "TEAM"

            if self.stats[player]['position'] == "TEAM":
                self.stats[player]['name'] = player  # assigns the TEAM_ key as the name
                self.stats[player]['age'] = None
            elif self.stats[player]['position'] == "DEF":
                self.stats[player]['name'] = f"{players.all_players[player]['first_name']} " \
                                             f"{players.all_players[player]['last_name']}"
                self.stats[player]['age'] = None
            else:
                self.stats[player]['name'] = players.all_players[player]['full_name']
                self.stats[player]['age'] = players.all_players[player]['age']

    def make_stats_list(self):
        self.stats_list = [values for player, values in self.stats.items()]

    def get_custom_score(self):
        # method to calculate customized score from league scoring settings
        if self.scoring_settings:
            for player in self.stats:
                score = 0.0
                for k, v in self.scoring_settings.items():
                    try:
                        score += self.stats[player][k] * self.scoring_settings[k]
                    except KeyError:
                        pass
                self.stats[player]["pts_custom"] = round(score, 2)
                try:
                    self.stats[player]["ppg"] = round(score / self.stats[player]["gp"], 2)
                except KeyError:
                    pass
        else:
            pass

    def fix_empty_scores(self):
        for p in self.stats:
            if "pts_ppr" in self.stats[p].keys():
                pass
            else:
                self.stats[p]["pts_ppr"] = 0.0
            if "pts_std" in self.stats[p].keys():
                pass
            else:
                self.stats[p]["pts_std"] = 0.0

    def get_all_projections(self, season_type, season):
        return self._call("{}/{}/{}".format(self._projections_base_url, season_type, season))

    def get_week_projections(self, season_type, season, week):
        return self._call("{}/{}/{}/{}".format(self._projections_base_url, season_type, season, week))

    def get_player_week_stats(self, stats, player_id):
        try:
            return stats[player_id]
        except KeyError:
            return None

    def get_player_week_score(self, stats, player_id):
        # TODO: Need to cache stats by week, to avoid continuous api calls
        result_dict = {}
        try:
            player_stats = stats[player_id]
        except KeyError:
            return None

        if stats:
            try:
                result_dict["pts_ppr"] = player_stats["pts_ppr"]
            except KeyError:
                result_dict["pts_ppr"] = None

            try:
                result_dict["pts_std"] = player_stats["pts_std"]
            except KeyError:
                result_dict["pts_std"] = None

            try:
                result_dict["pts_half_ppr"] = player_stats["pts_half_ppr"]
            except KeyError:
                result_dict["pts_half_ppr"] = None

            try:
                result_dict["pts_custom"] = player_stats["pts_custom"]
            except KeyError:
                result_dict["pts_custom"] = None
        return result_dict

    def check_local_cache(self):
        pass

    def delete_cache(self):
        pass

    def add_weekly_rank(self, stats_sorted):
        # TODO: convert to method and test
        # get rank of player's weekly finish, add that to player dict
        # add up score
        for week in stats_sorted:
            rank_counter = 0
            for player in week:
                rank_counter += 1
                week[player]['weekly_rank'] = rank_counter
                pos = week[player]['position']
                week[player]['stud'] = 0
                week[player]['start1'] = 0
                week[player]['start2'] = 0
                week[player]['bust'] = 0

                if rank_counter in range(1, 4):
                    # pdb.set_trace()
                    week[player]['stud'] = 1
                elif rank_counter in range(4, 13):
                    week[player]['start1'] = 1
                elif rank_counter in range(13, 25):
                    week[player]['start2'] = 1
                elif 'gp' in week[player].keys():
                    week[player]['bust'] = 1
                else:
                    week[player]['bust'] = 0

        return stats_sorted


