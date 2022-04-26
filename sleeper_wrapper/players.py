from .base_api import BaseApi
import json
import os


class Players(BaseApi):
    def __init__(self):
        pass

    def get_all_players(self):
        path = 'data/players'
        file = 'all_players.json'
        rel_path = path + "/" + file

        if os.path.exists(path) and os.path.isfile(path + "/" + file):
            print("Local path and file exists, reading local version")
            with open(rel_path) as json_file:
                all_players = json.load(json_file)
        else:
            print("local path and file not found, making API call")
            os.makedirs(path)
            all_players = self._call("https://api.sleeper.app/v1/players/nfl")
            with open(rel_path, 'w') as outfile:
                json.dump(all_players, outfile)

        # on exception, do API call and store the JSON in data/players
        """
        except FileNotFoundError:
            rel_path = "data/players/all_players.json"
            with open(rel_path, 'w') as outfile:
                json.dump(all_players, outfile)
        """
        return all_players

    def get_saved_players(self):
        with open('data/all_players.json') as json_file:
            all_players = json.load(json_file)
        return all_players

    def save_all_players(self):

        all_players = self._call("https://api.sleeper.app/v1/players/nfl")
        rel_path = "data/all_players.json"

        with open(rel_path, 'w') as outfile:
            json.dump(all_players, outfile)

        return all_players  # self._call("https://api.sleeper.app/v1/players/nfl")

    def get_trending_players(self, sport, add_drop, hours=24, limit=25):
        return self._call(
            "https://api.sleeper.app/v1/players/{}/trending/{}?lookback_hours={}&limit={}".format(sport, add_drop,
                                                                                                  hours, limit))