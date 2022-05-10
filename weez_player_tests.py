from sleeper_wrapper import League, Players, Stats
import time
import pandas as pd

league_id = 650057741137690624
league = League(league_id)
league.get_league()
players = Players()
# all_players = players.get_all_players()
stats = Stats()


print(players.all_players)
# players.check_cache()
# stats.get_custom_score(stats_2019, league.scoring_settings)
# stats.add_player_info(stats_2019)
# weez_rosters = league.get_rosters()

# test_stats = stats.get_week_stats(season=2020, week=10)
# test_custom_score = stats.get_custom_score(test_stats, league.scoring_settings)
# ss, sl = stats.get_stats_range(2021, 10, 10, league.scoring_settings, position_list=["TE"])


# print(f"od: {type(ss)}, sl: {type(sl)}")
# print(f"od: {type(ss)[0]} sl: {type(sl)[0]}")
# print(df.head())
# print(type(ss[0]))


# pd.set_option('display.max_columns', 40)
# df = pd.DataFrame()
"""
print(type(sl[0]))
df = pd.DataFrame.from_dict(ss[0], orient="index")
first_column = df.pop('name')
second_column = df.pop('pts_custom')
third_column = df.pop('pts_ppr')
df.insert(0, 'name', first_column)
df.insert(1, 'pts_custom', second_column)
df.insert(2, 'pts_ppr', third_column)
df.sort_values(by=['pts_custom'], ascending=False, inplace=True)
print(df.head())"""
