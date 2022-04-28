from sleeper_wrapper import League, Players, Stats
import time

league_id = 650057741137690624
league = League(league_id)
weez_league = league.get_league()
players = Players()
stats = Stats()
scoring_weights=weez_league['scoring_settings']

'''
start = time.time()
all_players = players.get_all_players()
end = time.time()
print(end - start)
'''

'''
start = time.time()
#all_players = players.get_all_players()
players.check_cache()
end = time.time()
print(end - start)
'''
def time_func(func):
    start = time.time()
    func
    end = time.time()
    print(end - start)
    pass
# time_func(players.get_all_players())
#time_func(stats.get_all_stats(2020))

# stats_2021 = stats.get_all_stats(2020)

week_1_2021 = stats.get_week_stats(2021, 1)

for stat in week_1_2021:
    print(week_1_2021[stat])