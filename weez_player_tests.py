from sleeper_wrapper import League, Players, Stats
import time

league_id = 650057741137690624
league = League(league_id)
league.get_league()
players = Players()
stats = Stats()

rosters = league.get_rosters()

print(league.scoring_settings)
print(league.name)
print(league.settings)

for r in rosters:
    print(r['team_name'])
# time_func(players.get_all_players())
# time_func(stats.get_all_stats(2020))

# stats_2021 = stats.get_all_stats(2020)

# week_1_2021 = stats.get_week_stats(2021, 1)

# stats.get_custom_score(weez_league.scoring_settings)

