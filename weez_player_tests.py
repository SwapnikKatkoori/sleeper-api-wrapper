import os
from sleeper_wrapper import League, Players, Stats
import time

league_id = 650057741137690624
league = League(league_id)
league.get_league()
players = Players()
stats = Stats()


weez_rosters = league.get_rosters()
all_players = players.get_all_players()

for player in all_players:
    try:
        print(all_players[player].first_name)
    except AttributeError:
        pass


"""
for player in all_players:
    cp = all_players[player]
    if "years_exp" in cp.keys() and cp['years_exp'] == 0:
        if cp["position"] == "WR":
            print(cp["first_name"] + " " + cp["last_name"])
    else:
        pass
"""


# print(len(all_players))

