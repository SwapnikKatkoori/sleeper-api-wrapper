import pdb
from collections import Counter, OrderedDict
from sleeper_wrapper.base_api import BaseApi
from sleeper_wrapper.players import Players, Player
from operator import getitem
import json
from pathlib import Path
import pandas as pd

class Stats(BaseApi):
    def __init__(self):
        self._base_url = "https://api.sleeper.app/v1/stats/{}".format("nfl")
        self._projections_base_url = "https://api.sleeper.app/v1/projections/{}".format("nfl")
        self._full_stats = None

    def get_player_info(self):
        pass

    def get_yearly_stats(self, season, season_type="regular"):
        dir_path = Path(f'data/stats/{season}')
        file_path = Path(f'data/stats/{season}/all_stats_{season}')

        if dir_path.exists() and file_path.exists():
            # if path and file are there, open local instance
            print("Local path and file exists, reading local version")
            with open(file_path) as json_file:
                all_year_stats = json.load(json_file)
        else:
            # if path or file not there, do API call and store the JSON
            print("local path and file not found, making API call")
            dir_path.mkdir(parents=True, exist_ok=True)
            all_year_stats = self._call("{}/{}/{}".format(self._base_url, season_type, season))
            with open(file_path, 'w') as outfile:
                json.dump(all_year_stats, outfile)

        return all_year_stats

    def get_week_stats(self, season, week, season_type="regular"):
        dir_path = Path(f'data/stats/{season}')
        file_path = Path(f'data/stats/{season}/week_{week:02d}_stats_{season}')
        if dir_path.exists() and file_path.exists():
            with open(file_path) as json_file:
                week_stats = json.load(json_file)
        else:
            # make API call if local JSON is not found
            print("local path and file not found, making API call")
            dir_path.mkdir(parents=True, exist_ok=True)
            week_stats = self._call("{}/{}/{}/{}".format(self._base_url, season_type, season, week))
            with open(file_path, 'w') as outfile:
                json.dump(week_stats, outfile)

        return week_stats

    def get_all_projections(self, season_type, season):
        return self._call("{}/{}/{}".format(self._projections_base_url, season_type, season))

    def get_week_projections(self, season_type, season, week):
        return self._call("{}/{}/{}/{}".format(self._projections_base_url, season_type, season, week))

    def get_player_week_stats(self, stats, player_id):
        try:
            return stats[player_id]
        except:
            return None

    def get_player_week_score(self, stats, player_id):
        # TODO: Need to cache stats by week, to avoid continuous api calls
        result_dict = {}
        try:
            player_stats = stats[player_id]
        except:
            return None

        if stats:
            try:
                result_dict["pts_ppr"] = player_stats["pts_ppr"]
            except:
                result_dict["pts_ppr"] = None

            try:
                result_dict["pts_std"] = player_stats["pts_std"]
            except:
                result_dict["pts_std"] = None

            try:
                result_dict["pts_half_ppr"] = player_stats["pts_half_ppr"]
            except:
                result_dict["pts_half_ppr"] = None

        return result_dict

    def get_custom_score(self, stats, scoring_settings):
        # method to calculate customized score
        # from scoring weights and stats dict
        """
        for player_id in stats:
        """
        score = 0.0
        for k, v in scoring_settings.items():
            try:
                score += stats[k] * scoring_settings[k]
            except KeyError:
                pass
        stats["pts_custom"] = round(score, 2)
        score = round(score, 2)
        return score

    def get_stats_range(self, year, start_week, stop_week, scoring_settings,
                        position_list=['QB', 'RB', 'WR', 'TE', 'DEF']):
        # # TODO: need to change into method and test or add range to get_weekly_stats
        # function to grab list of weekly stats from stats
        # bring in stats.get_week_stats
        # adds the custom score from the get_custom_score func

        stats_list = []
        players = Players()
        df = pd.DataFrame()

        for x in range(start_week, stop_week + 1):
            current_week = self.get_week_stats(year, x)
            # pdb.set_trace()
            trimmed_week = {}
            # for loop to calculate the custom points
            for player in current_week:
                # try block to get custom points
                try:
                    current_week[player]['pts_custom'] = self.get_custom_score(current_week[player], scoring_settings)
                    # try to get position, name, team of current player - trim those that aren't in the position?
                    current_week[player]['position'] = players.all_players[player]['position']
                except KeyError:
                    current_week[player]['position'] = 'TEAM'

                # next try loop to get the player name
                try:
                    current_week[player]['name'] = players.all_players[player]['full_name']
                except KeyError:
                    try:
                        current_week[player]['name'] = f"{players.all_players[player]['first_name']} " \
                                                       f"{players.all_players[player]['last_name']}"
                    except KeyError:
                        current_week[player]['name'] = player
                # now that we've added the position, we can add just the positions to the trim week
                if current_week[player]['position'] in position_list:
                    # pdb.set_trace()
                    trimmed_week[player] = current_week[player]
                else:
                    pass
            stats_list.append(trimmed_week)  # unsorted list returned
            # df = df.append(trimmed_week, ignore_index=True)
        # time to sort the stats_list with OrderedDict
        stats_sorted = []

        for s in stats_list:
            res = OrderedDict(
                sorted(s.items(), key=lambda x: getitem(x[1], 'pts_custom'), reverse=True))
            stats_sorted.append(res)

        return stats_sorted, stats_list

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

    def get_stats_totals(self, stats_sorted):
        # TODO: convert to method and test
        # take sorted stats list and add all columns
        # goal is to return single dict ordered by column choice

        totals_dict = {}

        for week in stats_sorted:
            for player in week:
                if player not in totals_dict:
                    totals_dict[player] = week[player]
                else:
                    for k, v in week[player].items():
                        if k not in totals_dict[player]:
                            totals_dict[player][k] = v
                        elif (k == 'position') or (k == 'name'):
                            # pdb.set_trace()
                            pass
                        else:
                            totals_dict[player][k] += v

        return totals_dict
