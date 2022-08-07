"""
Get projections and rankings from fantasypros.
"""
import pdb
import re
import pandas as pd
from pathlib import Path
from sleeper_wrapper import League, Players
import json
import time

league = League()
players = Players()
players = players.get_all_players()
"""

"""


class Projections:
    def __init__(self, scoring_keys=league.scoring_settings):
        self.qb_path = Path("data/fpros/FantasyPros_Fantasy_Football_Projections_QB.csv")
        self.flex_path = Path("data/fpros/FantasyPros_Fantasy_Football_Projections_FLX.csv")
        self.scoring_keys = scoring_keys
        # ----- Projections and VBD -------#
        self.qb_df = self.clean_qb_df()
        self.flex_df, self.rb_df, self.wr_df, self.te_df = self.clean_flex_df()
        # ------ ECR rankings for SuperFlex, and positional ------- #
        self.ecr_sf_df, self.ecr_qb_df, self.ecr_rb_df, self.ecr_wr_df, self.ecr_te_df = self.get_ecr_rankings()
        self.all_df = self.get_all_df()
        self.list_of_player_dicts = self.all_df.to_dict("records")

    def get_all_df(self):
        # all_df refers to the projections and VBD dataframes
        # Stack the positonial projection dataframes on top of each each other,
        all_df = pd.concat([self.qb_df, self.rb_df, self.wr_df, self.te_df]).fillna(0)
        all_df.drop(all_df[all_df['name'] == 0].index, inplace=True)
        # ---- Sorting the all_dfs by VBD to add overall VBD ranking ------ #
        all_df = self.sort_reset_index(all_df)
        all_df.sort_values(by="vbd", ascending=False, inplace=True)
        all_df.reset_index(drop=True, inplace=True)
        all_df["overall_vbd_rank"] = all_df.index + 1

        # Now merge the all_df(vbd/projections) with the ECR superflex
        all_df = pd.merge(all_df, self.ecr_sf_df, how="left", on="name", suffixes=('', '_y'))
        all_df.drop(all_df.filter(regex='_y$').columns, axis=1, inplace=True)

        # now take all values to get the sleeper_ids
        print(len(all_df))
        print("Looking up sleeper Values")
        start = time.time()
        all_df = self.get_sleeper_ids(all_df)
        end = time.time()
        print(f"Total time to lookup Sleeper Values: {end - start} seconds")



        return all_df

    def sort_reset_index(self, df):
        """
        This gets called every time we add vbd to sort by vbd and reset the index
        """
        df.sort_values(by=["vbd", "fpts"], ascending=False, inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df

    def get_custom_score_row(self, row):
        score = 0
        for k, v in self.scoring_keys.items():
            try:
                score += self.scoring_keys[k] * row[k]
            except KeyError:
                pass
        return score

    def clean_qb_df(self):
        qb_df = pd.read_csv(self.qb_path, skiprows=[1])

        # lower case all column names
        qb_df.columns = qb_df.columns.str.lower()

        qb_df.rename(columns={"tds": "pass_td",
                              "ints": "pass_int",
                              "att": "pass_att",
                              "att.1": "rush_att",
                              "yds": "pass_yd",
                              "yds.1": "rush_yd",
                              "tds.1": "rush_td",
                              "fl": "fum_lost",
                              "player": "name"}, inplace=True)
        qb_df["position_rank_projections"] = qb_df.index + 1

        # remove non-numeric (commas) characters from the number fields
        qb_df.replace(',', '', regex=True, inplace=True)
        qb_df["pass_yd"] = qb_df["pass_yd"].apply(pd.to_numeric)

        # calculate custom score and sort
        qb_df["fpts"] = qb_df.apply(self.get_custom_score_row, axis=1)
        # add position field needed before we can send to add_vbd
        qb_df["position"] = "QB"
        # send to add_vbd
        qb_df = self.add_vbd(qb_df)
        # add position and rank columns
        qb_df["pos_rank"] = "QB" + qb_df["position_rank_vbd"].astype(str)
        return qb_df

    def clean_flex_df(self):
        """
        Take the single Flex CSV, clean up the column names, add the position and bonus
        columns, get custom score, split into positional DataFrames, and add VBD
        """
        flex_df = pd.read_csv(self.flex_path, skiprows=[1])  # skips the first blank row
        flex_df.columns = flex_df.columns.str.lower()
        flex_df["position"] = flex_df["pos"].str[:2]
        flex_df["position_rank_projections"] = flex_df["pos"].str[2:]
        flex_df["bonus_rec_te"] = flex_df["rec"].loc[flex_df["position"] == "TE"]
        flex_df["bonus_rec_te"] = flex_df['bonus_rec_te'].fillna(0)
        flex_df.rename(columns={"player": "name",
                                "pos": "pos_rank",
                                "att": "rush_att",
                                "tds": "rush_td",
                                "yds": "rush_yd",
                                "yds.1": "rec_yd",
                                "tds.1": "rec_td",
                                "team": "team",
                                "fpts": "fpts",
                                "rec": "rec",
                                "fl": "fum_lost"}, inplace=True)

        # remove non numeric characters from the number fields
        flex_df.replace(',', '', regex=True, inplace=True)
        flex_df["rec_yd"] = flex_df["rec_yd"].apply(pd.to_numeric)
        flex_df["rush_yd"] = flex_df["rush_yd"].apply(pd.to_numeric)

        # calculate custom score and sort
        flex_df["fpts"] = flex_df.apply(self.get_custom_score_row, axis=1)
        flex_df.sort_values(by="fpts", inplace=True, ascending=False)

        # split into RB, WR, and TE DFs, return all 4
        rb_df = flex_df[flex_df["position"] == "RB"]
        rb_df = self.add_vbd(rb_df)
        wr_df = flex_df[flex_df["position"] == "WR"]
        wr_df = self.add_vbd(wr_df)
        te_df = flex_df[flex_df["position"] == "TE"]
        te_df = self.add_vbd(te_df)

        return flex_df, rb_df, wr_df, te_df

    def add_vbd(self, df):
        # get thresholds
        try:
            if df.iloc[1]['position'] == 'QB':
                vols_threshold = df.iloc[25]['fpts']
                vorp_threshold = df.iloc[31]['fpts']
            elif df.iloc[1]['position'] == 'RB':
                vols_threshold = df.iloc[25]['fpts']
                vorp_threshold = df.iloc[55]['fpts']
            elif df.iloc[1]['position'] == 'WR':
                vols_threshold = df.iloc[25]['fpts']
                vorp_threshold = df.iloc[63]['fpts']
            elif df.iloc[1]['position'] == 'TE':
                vols_threshold = df.iloc[10]['fpts']
                vorp_threshold = df.iloc[22]['fpts']
        except KeyError:
            print("Key Error in FPros Add VBD Func")

        # TODO Figure out this chained_assignment issue with the error message of:
        #       SettingWithCopyError:
        #       A value is trying to be set on a copy of a slice from a DataFrame.
        #       Try using .loc[row_indexer,col_indexer] = value instead
        pd.options.mode.chained_assignment = None
        df["vols"] = df.apply(lambda row: self.calc_vols(row, vols_threshold), axis=1)
        df["vorp"] = df.apply(lambda row: self.calc_vorp(row, vorp_threshold), axis=1)
        df["vbd"] = df.apply(lambda row: self.calc_vbd(row), axis=1)
        df['vona'] = df.fpts.diff(periods=-1)
        df = self.sort_reset_index(df)
        df["position_rank_vbd"] = df.index + 1
        return df

    def calc_vols(self, row, vols_threshold):
        return max(0, row['fpts'] - vols_threshold)

    def calc_vorp(self, row, vorp_threshold):
        return max(0, row['fpts'] - vorp_threshold)

    def calc_vbd(self, row):
        return max(0, row['vols'] + row['vorp'])

    def get_ecr_rankings(self):
        """
        Return single dataframe with columns for superflex_rank, suplerflex_tier,
        and pos_rank, pos_tier.  Also modify the self.dfs for projections.
        self.flex_df, self.rb_df, self.wr_df, self.te_df = self.clean_flex_df()
        """
        # pd.set_option('display.max_columns', None)

        sf_rank_path = Path("data/fpros/FantasyPros_2022_Draft_SuperFlex_Rankings.csv")
        ecr_sf_df = pd.read_csv(sf_rank_path)
        ecr_sf_df.drop(columns="ECR VS. ADP", inplace=True)

        ecr_sf_df.rename(columns={"RK": "superflex_rank_ecr",
                                  "TIERS": "superflex_tier_ecr",
                                  "PLAYER NAME": "name",
                                  "TEAM": "team",
                                  "POS": "pos_rank",
                                  "BYE WEEK": "bye",
                                  "SOS SEASON": "sos_season"}, inplace=True)

        # do positional rankings now, combining them with single ECR DF
        # create dict to rename positional columns
        ecr_col_changes = {"RK": "position_rank_ecr", "TIERS": "position_tier_ecr", "PLAYER NAME": "name",
                           "TEAM": "team",
                           "POS": "position",
                           "BYE WEEK": "bye",
                           "SOS SEASON": "sos_season",
                           "ECR VS. ADP": "ecr_vs_adp"}
        ecr_qb_df = pd.read_csv("data/fpros/FantasyPros_2022_Draft_QB_Rankings.csv")
        ecr_rb_df = pd.read_csv("data/fpros/FantasyPros_2022_Draft_RB_Rankings.csv")
        ecr_wr_df = pd.read_csv("data/fpros/FantasyPros_2022_Draft_WR_Rankings.csv")
        ecr_te_df = pd.read_csv("data/fpros/FantasyPros_2022_Draft_TE_Rankings.csv")
        ecr_qb_df["position"] = "QB"
        ecr_rb_df["position"] = "RB"
        ecr_wr_df["position"] = "WR"
        ecr_te_df["position"] = "TE"
        ecr_df_list = [ecr_qb_df, ecr_rb_df, ecr_wr_df, ecr_te_df]
        for ecr_df in ecr_df_list:
            ecr_df.rename(columns=ecr_col_changes, inplace=True)
        pd.set_option("display.max_column", None)
        position_ecr_combined_df = pd.concat(ecr_df_list).fillna(0)
        cols_to_use = position_ecr_combined_df.columns.difference(ecr_sf_df.columns).to_list()
        cols_to_use.append("name")
        ecr_sf_df = pd.merge(ecr_sf_df, position_ecr_combined_df[cols_to_use], how="outer", on="name")
        return ecr_sf_df, ecr_qb_df, ecr_rb_df, ecr_wr_df, ecr_te_df


    def get_sleeper_ids(self, df):
        start_time = time.time()
        # ----- Create the search_names (all lowercase, no spaces) ------ #
        search_names = []
        for idx, row in df.iterrows():
            if row["team"] == "JAC":
                df.loc[idx, "team"] = "JAX"
            new_name = re.sub(r'\W+', '', row['name']).lower()
            if new_name[-2:] == "jr":
                new_name = new_name[:-2]
            elif new_name[-3:] == "iii":
                new_name = new_name[:-3]
            elif new_name[-2:] == "ii":
                new_name = new_name[:-2]

            if new_name == "mitchelltrubisky":
                new_name = "mitchtrubisky"
            if new_name == "kennethwalker":
                new_name = "kenwalker"
            search_names.append(new_name)

        df['search_full_name'] = search_names
        search_name_tuples = list(zip(df.search_full_name, df.team))

        players = Players()
        players_df = players.get_players_df(['QB', 'RB', 'WR', 'TE'])
        players_match_df = players_df[players_df[['search_full_name', 'team']].apply(tuple, axis=1).isin(search_name_tuples)]
        cols_to_use = players_match_df.columns.difference(df.columns).to_list()
        cols_to_use.append("search_full_name")
        df = pd.merge(df, players_match_df[cols_to_use], how="left", on="search_full_name")
        for index, row in df.iterrows():
            if row["position"] == "DEF":
                df.loc[index, "sleeper_id"] = row["team"]
            else:
                df.loc[index, "sleeper_id"] = row["player_id"]
        # df['sleeper_id'] = df.apply(lambda x: x['team'] if x['player_id'] is None else x['player_id'], axis=1)
        match_search_names = df['search_full_name'].to_list()
        missing_search_names = [n for n in search_names if n not in match_search_names]
        if missing_search_names:
            print(f"Missing Search Names: {missing_search_names}")
        """
        df = players_df[players_df[['search_full_name', 'team']].apply(tuple, axis=1).isin(search_name_tuples)]
        match_search_names = df['search_full_name'].to_list()

        missing_search_names = [n for n in search_names if n not in match_search_names]
        end_time = time.time()
        print(f"Missing Search Names: {missing_search_names}")
        print(f"Total Time to get Sleeper IDs{end_time - start_time}")
        """
        return df
        """
        # ------ Now iterate over the player the dataframe and dictionary to look up and match sleeper id -----#
        for index, row in df.iterrows():
            cur_name = row["search_full_name"]
            if "sleeper_id" in row.index:
                pass
            elif row["position"] == "DEF":
                row["sleeper_id"] = row["team"]

            match = False
            for k, v in players.items():
                if "search_full_name" in v.keys():
                    if v["search_full_name"] == cur_name:
                        if v["team"] == row["team"]:
                            df.loc[index, "sleeper_id"] = k
                            match = True
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
            if not match:
                print(f"FPros: No Match on {row['search_full_name']}")
        print(df.loc[df['sleeper_id'].isna()])
        # pdb.set_trace()
        return df
        """


"""        
projections = Projections()
p = projections.list_of_player_dicts
print(p)
with open('data/fpros/fpros_players_dicts.json', 'w') as file:
    json.dump(p, file, indent=4)
"""