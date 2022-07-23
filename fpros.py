"""
Get projections and rankings from fantasypros.
"""
import pdb
import re
import pandas as pd
from pathlib import Path
from sleeper_wrapper import League, Players
import json

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
        self.qb_df = self.clean_qb_df()
        self.flex_df, self.rb_df, self.wr_df, self.te_df = self.clean_flex_df()
        self.ecr_sf_df, self.ecr_qb_df, self.ecr_rb_df, self.ecr_wr_df, self.ecr_te_df = self.get_ecr_rankings()
        self.all_df = self.get_all_df()
        self.dict = self.all_df.to_dict("records")

    def get_all_df(self):
        all_df = pd.concat([self.qb_df, self.rb_df, self.wr_df, self.te_df]).fillna(0)
        all_df.drop(all_df[all_df['name'] == 0].index, inplace=True)
        all_df = self.sort_reset_index(all_df)
        all_df.sort_values(by="vbd", ascending=False, inplace=True)
        all_df.reset_index(drop=True, inplace=True)
        all_df["overall_vbd_rank"] = all_df.index + 1
        all_df = pd.merge(all_df, self.ecr_sf_df, how="left", on="name", suffixes=('', '_y'))
        all_df.drop(all_df.filter(regex='_y$').columns, axis=1, inplace=True)
        all_df = self.get_sleeper_ids(all_df)
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
            pdb.set_trace()

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
        # create dict to rename positional columns
        ecr_col_changes = {"RK": "position_rank_ecr", "TIERS": "position_tier_ecr", "PLAYER NAME": "name", "TEAM": "team",
                           "POS": "position",
                           "BYE WEEK": "bye",
                           "SOS SEASON": "sos_season",
                           "ECR VS. ADP": "ecr_vs_adp"}
        ecr_sf_df.rename(columns={"RK": "superflex_rank_ecr",
                               "TIERS": "superflex_tier_ecr",
                               "PLAYER NAME": "name",
                               "TEAM": "team",
                               "POS": "position",
                               "BYE WEEK": "bye",
                               "SOS SEASON": "sos_season",
                               "ECR VS. ADP": "ecr_vs_adp"}, inplace=True)

        # do positional rankings now, combining them with single ECR DF
        ecr_qb_df = pd.read_csv("data/fpros/FantasyPros_2022_Draft_QB_Rankings.csv")
        ecr_rb_df = pd.read_csv("data/fpros/FantasyPros_2022_Draft_RB_Rankings.csv")
        ecr_wr_df = pd.read_csv("data/fpros/FantasyPros_2022_Draft_WR_Rankings.csv")
        ecr_te_df = pd.read_csv("data/fpros/FantasyPros_2022_Draft_TE_Rankings.csv")

        ecr_df_list = [ecr_qb_df, ecr_rb_df, ecr_wr_df, ecr_te_df]
        for ecr_df in ecr_df_list:
            ecr_df.rename(columns=ecr_col_changes, inplace=True)

        return ecr_sf_df, ecr_qb_df, ecr_rb_df, ecr_wr_df, ecr_te_df

    def get_sleeper_ids(self, df):

        # ----- Create the search_names (all lowercase, no spaces) ------ #
        search_names = []
        for idx, row in df.iterrows():
            new_name = re.sub(r'\W+', '', row['name']).lower()
            if new_name[-2:] == "jr":
                new_name = new_name[:-2]
                print(new_name)
            elif new_name[-3:] == "iii":
                new_name = new_name[:-3]
            elif new_name[-2:] == "ii":
                new_name = new_name[:-2]
            search_names.append(new_name)

        df['search_full_name'] = search_names

        # ------ Now iterate over the player the dataframe and dictionary to look up and match sleeper id -----#
        count = 0
        for index, row in df.iterrows():
            cur_name = row["search_full_name"]
            if "sleeper_id" in row.index:
                pass
            elif row["position"] == "DEF":
                row["sleeper_id"] = row["team"]
            else:
                for k, v in players.items():
                    if "search_full_name" in v.keys():
                        if v["search_full_name"] == cur_name:
                            if v["team"] == row["team"]:
                                df.loc[index, "sleeper_id"] = k
                        else:
                            pass
                    else:
                        pass
        return df

# TODO - 1. Calculate Tiers, 2. Match up with Sleeper IDs

projections = Projections()
df = projections.all_df
print(df.keys())
pdict = projections.dict
for p in pdict:
    print(p)
