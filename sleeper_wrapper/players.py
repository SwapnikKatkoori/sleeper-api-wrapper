from .base_api import BaseApi
import json
from pathlib import Path


class Players(BaseApi):
    def __init__(self):
        pass

    def get_all_players(self):
        dir_path = Path('data/players')
        file_path = Path('data/players/all_players.json')

        if file_path.exists() and dir_path.exists():
            print("Local path and file exists, reading local version")
            with open(file_path) as json_file:
                all_players = json.load(json_file)
        else:
            print("local path and file not found, making API call")
            dir_path.mkdir(parents=True, exist_ok=True)
            all_players = self._call("https://api.sleeper.app/v1/players/nfl")
            with open(file_path, 'w') as outfile:
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
    def check_cache(self):
        dir_path = Path('data/players')
        file_path = Path('data/players/all_players.json')

        print(f"Dir {dir_path} exists:  {dir_path.exists()}")
        print(f"File {file_path} exists: {file_path.exists()}")
        return dir_path.is_dir() and file_path.exists()