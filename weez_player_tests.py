import os
from sleeper_wrapper import League, Players, Stats
import time

league_id = 650057741137690624
league = League(league_id)
weez_league = league.get_league()
players = Players()
stats = Stats()


test_roster2 = league.get_rosters()

roster_keys = {}
for roster in test_roster2:
    print(roster.full_dict.keys())
