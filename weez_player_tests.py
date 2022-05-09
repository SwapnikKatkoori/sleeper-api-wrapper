from sleeper_wrapper import League, Players, Stats
import time

league_id = 650057741137690624
league = League(league_id)
league.get_league()
players = Players()
all_players = players.get_all_players()
stats = Stats()



# players.check_cache()
# stats.get_custom_score(stats_2019, league.scoring_settings)
# stats.add_player_info(stats_2019)
# weez_rosters = league.get_rosters()

# test_stats = stats.get_week_stats(season=2020, week=10)
# test_custom_score = stats.get_custom_score(test_stats, league.scoring_settings)
ts, df = stats.get_stats_range(2021, 1, 4, league.scoring_settings)


print(df)

"""week_num = 0
for d in test_stats_range:
    week_num += 1
    print(f"Week {week_num}")
    for p in d:
        print(d[p].keys())
        # print(f"{d[p]['name']} {d[p]['position']} {d[p]['pts_custom']} {d[p]['pts_ppr']}")

"""


