import pdb
import json
from sleeper_wrapper import League, Stats
# import pandas as pd

league_id = 650057741137690624
league = League(league_id)
league.get_league()
# stats = Stats(2020, week_start=1, week_stop=16)
stats = Stats(2018, week_start=1, week_stop=17, scoring_settings=league.scoring_settings)
td = stats.totals_dict

for p in td:
    if td[p]['gp'] == 2.0:
        print(td[p])
# stats_2021 = stats.get_year_stats(2021)

with open("league_settings.json", 'w') as outfile:
    json.dump(league.scoring_settings, outfile, indent=4)
# stats_odict, stats_list = stats.get_stats_range(2021, 9, 11, league.scoring_settings, position_list=["RB"])

# for p in stats_list:
#     key_set = set().union(*(p[player].keys() for player in p))

# key_list = list(key_set)

# key_list.sort()

# df = pd.DataFrame.from_dict(stats.stats, orient="index")
# df sle= df.transpose()
# stats_list = sorted([stats.stats[p] for p in stats.stats], key=lambda i: i["vbd_ppr"], reverse=True)

# stats_list = [p for p in stats.stats]
# stats_list = sorted(stats_list, "pos_rank_custom", reverse=True)


# print(stats.get_player_week_score(stats.stats, '5000'))
