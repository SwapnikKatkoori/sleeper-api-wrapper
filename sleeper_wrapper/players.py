from .base_api import BaseApi
import json
from pathlib import Path
import pandas as pd

class Player(object):

    # new init with bunching
    def __init__(self, player_dict):
        self.__dict__.update(player_dict)
        for k in player_dict:
            setattr(self, k, player_dict[k])
        self.name_position = f"{self.first_name} {self.last_name}, {self.position} {self.team}"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def __getitem__(self, item):
        return getattr(self, item)


        """    
    OLD init with dictionary comprehension
    def __init__(self, *player_dict, **kwargs):
        for dictionary in player_dict:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])
        self.name = f"{self.first_name} {self.last_name}"
        """


class Players(BaseApi):
    def __init__(self):
        self.dir_path = Path('data/players')
        self.file_path = Path('data/players/all_players.json')
        self.all_players = self.get_all_players()
        self.players_df = self.get_players_df()

    def get_players_df(self, position_list=['QB', 'RB', 'WR', 'TE', 'K', 'DEF']):
        df = pd.DataFrame.from_dict(self.all_players, orient="index")

        return df[df.position.isin(position_list)]

    def get_all_players(self):
        if self.file_path.exists() and self.dir_path.exists():
            print("Players Call: Local path and file exists, reading local version")
            with open(self.file_path) as json_file:
                all_players = json.load(json_file)
        else:
            print("Players Call: local path and file not found, making API call")
            self.dir_path.mkdir(parents=True, exist_ok=True)
            all_players = self._call("https://api.sleeper.app/v1/players/nfl")
            with open(self.file_path, 'w') as outfile:
                json.dump(all_players, outfile, indent=4)



        return all_players

    def make_player_objects(self, player_id_list):
        players_list = []
        for player_id in player_id_list:
            cur_player = Player(self.all_players[player_id])
            players_list.append(cur_player)
        return players_list

    def get_trending_players(self, sport, add_drop, hours=24, limit=25):
        return self._call(
            f"https://api.sleeper.app/v1/players/{sport}/trending/{add_drop}?lookback_hours={hours}&limit={limit}")

    def check_cache(self):
        print(f"Dir {self.dir_path} exists:  {self.dir_path.exists()}")
        print(f"File {self.file_path} exists: {self.file_path.exists()}")

    def delete_cache(self):
        self.file_path.unlink()
