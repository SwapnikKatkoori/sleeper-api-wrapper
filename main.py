"""

fantasy sleeper project

Display players and stats
Display League Info
Get stats leaders over any given week
show consistency ratings
Show Draft Pick Value
Create Draft Tracker
Split Stats into Basic Stats, Advanced Metrics


"""

from sleeper_wrapper import League, Players, Stats

league_id = 650057741137690624
league = League(league_id)
print(league.scoring_settings)
#league.get_league()
players = Players()

for p in players.all_players:
    try:
        if players.all_players[p]["position"] != "QB":
            print(players.all_players[p])
    except KeyError:
        pass


