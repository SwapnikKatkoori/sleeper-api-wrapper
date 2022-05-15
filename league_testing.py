import pdb

from sleeper_wrapper import League, Players

league_id = 650057741137690624

league = League(league_id)
# players = Players()

rosters = league.get_rosters()


key_errors = []
for roster in rosters:
    print(roster.players)

print(key_errors)
