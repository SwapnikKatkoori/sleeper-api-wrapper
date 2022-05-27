import pdb
from sleeper_wrapper.base_api import BaseApi
from sleeper_wrapper.players import Players
from operator import getitem
import json
from pathlib import Path
import pandas as pd


class Stats(BaseApi):
    def __init__(self, season=2021, season_type="regular", position_list=["QB", "RB", "WR", "TE", "DEF", "K"], **kwargs):
        self.season = season
        self.season_type = season_type
        self.position_list = position_list
        self.vbd_baselines = kwargs.get("vbd_baselines")
        self.scoring_settings = kwargs.get("scoring_settings")
        self.week_start = kwargs.get("week_start")
        self.week_stop = kwargs.get("week_stop")
        self.stats_list = []
        self._base_url = "https://api.sleeper.app/v1/stats/{}".format("nfl")
        self._projections_base_url = "https://api.sleeper.app/v1/projections/{}".format("nfl")
        self._full_stats = None
        self.stats = self.get_stats()
        self.df = pd.DataFrame(self.stats_list)

    def trim_to_positions(self):
        self.stats = {
            k: v for k, v in self.stats.items()
            if self.stats[k]["position"] in self.position_list and "gp" in self.stats[k].keys()
        }

    def add_pos_rank_custom(self, scoring_type):
        # TODO: Fix this to get position ranks
        list_to_sort = sorted([self.stats[p] for p in self.stats], key=lambda i: i[f"pts_{scoring_type}"], reverse=True)
        rank_counter = 1
        for players in list_to_sort:
            players["pos_rank_custom"] = rank_counter
            rank_counter += 1
        print(list_to_sort)

    def add_rank_custom(self, scoring_type):
        # pdb.set_trace()
        list_to_sort = sorted([self.stats[p] for p in self.stats], key=lambda i: i[f"pts_{scoring_type}"], reverse=True)
        rank_counter = 1
        for players in list_to_sort:
            players[f"rank_{scoring_type}"] = rank_counter
            rank_counter += 1

    def add_vbd(self):
        # compare player's score with X score at that position
        # get baselines
        self.vbd_baselines = {'RB': 24, 'QB': 24, 'WR': 36, 'TE': 12, 'K': 12, 'DEF': 12}
        pass


    def map_player_info(self):
        # Adds player name, age and position to stats_dict json for saving
        players = Players()
        for player in self.stats:
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

    def get_stats(self) -> object:
        if self.week_start:
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
            if self.scoring_settings:
                self.get_custom_score()
                self.add_rank_custom("custom")
            self.add_vbd()
        return self.stats

    def get_week_stats(self):
        if not self.week_stop:
            self.week_stop = self.week_start
        if self.week_stop < self.week_start:
            print("Sorry, end week is before start")
            return {}

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
                self.add_rank_custom("ppr")
                self.add_rank_custom("std")
                if self.scoring_settings:
                    self.get_custom_score()
                    self.add_rank_custom("custom")

                self.stats_list.append(self.stats)

        self.stats = self.get_stats_totals()
        self.stats = self.get_stats_average()
        return self.stats

    def get_stats_average(self):
        exclude_keys = ["position", "name", "age", "gp", "gms_active", "pts_ppr", "pts_custom", "pos_rank_custom"]
        for p in self.stats:
            if "gp" in self.stats[p].keys():
                games_played = self.stats[p]["gp"]
                for k, v in self.stats[p].items():
                    if type(v) == str or k in exclude_keys:
                        pass
                    else:
                        self.stats[p][k] = round(v / games_played, 2)
            else:
                pass
        return self.stats

    def get_stats_totals(self):
        # TODO: work on keys to exclude from totalling
        # take sorted stats list and add all columns
        # goal is to return single dict ordered by column choice
        totals_dict = {}
        exclude_keys = ["position", "name", "age"]
        for week in self.stats_list:
            for player in week:
                if player not in totals_dict:
                    totals_dict[player] = week[player]
                else:
                    for k, v in week[player].items():
                        if k not in totals_dict[player]:
                            totals_dict[player][k] = round(v, 2)
                        elif k in exclude_keys:
                            pass
                        else:
                            totals_dict[player][k] += round(v, 2)
        return totals_dict

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


