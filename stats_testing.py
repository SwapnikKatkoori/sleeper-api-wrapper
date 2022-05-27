import pdb

from sleeper_wrapper import League, Stats
# import pandas as pd

league = League()
# stats = Stats(2020, week_start=1, week_stop=16)
stats = Stats(2020, scoring_settings=league.scoring_settings)
# stats_2021 = stats.get_year_stats(2021)


# stats_odict, stats_list = stats.get_stats_range(2021, 9, 11, league.scoring_settings, position_list=["RB"])

# for p in stats_list:
#     key_set = set().union(*(p[player].keys() for player in p))

# key_list = list(key_set)

# key_list.sort()
print(len(stats.stats))
# df = pd.DataFrame.from_dict(stats.stats, orient="index")
# df sle= df.transpose()
# stats_list = sorted([stats.stats[p] for p in stats.stats], key=lambda i: i["vbd_ppr"], reverse=True)

# stats_list = [p for p in stats.stats]
# stats_list = sorted(stats_list, "pos_rank_custom", reverse=True)
for cp in stats_list:
    if cp['vbd_ppr'] > 0:
        print(f"{cp['name']}, total_points: {cp['pts_ppr']}, vbd_ppr: {cp['vbd_ppr']}")



# print(stats.get_player_week_score(stats.stats, '5000'))
