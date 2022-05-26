from sleeper_wrapper import League, Stats
import pandas as pd

league = League()
# stats = Stats(2020, week_start=1, week_stop=16)
stats = Stats(2018, week_start=2, scoring_settings=league.scoring_settings, position_list=["QB"])
# stats_2021 = stats.get_year_stats(2021)


# stats_odict, stats_list = stats.get_stats_range(2021, 9, 11, league.scoring_settings, position_list=["RB"])

# for p in stats_list:
#     key_set = set().union(*(p[player].keys() for player in p))

# key_list = list(key_set)

# key_list.sort()
print(len(stats.stats))
# df = pd.DataFrame.from_dict(stats.stats, orient="index")
# df sle= df.transpose()
for p in stats.stats:
    if "gp" in stats.stats[p]:
        print(stats.stats[p])
