import pdb
import re
import pandas as pd
from pathlib import Path
import time
from pandastable import Table
from tkinter import *
from ffcalc import get_sleeper_ids, get_adp_df

def get_ecr_rankings(player_count=225):
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
    ecr_sf_df = pd.merge(ecr_sf_df.loc[:player_count], position_ecr_combined_df[cols_to_use], how="left", on="name")
    # pdb.set_trace()
    ecr_sf_df = get_sleeper_ids(ecr_sf_df)
    return ecr_sf_df

def clean_qb_df(qb_df):
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
    qb_df["position"] = "QB"
    qb_df["pos_rank"] = qb_df["position"] + qb_df["position_rank_projections"].astype(str)

    qb_df.dropna(inplace=True, thresh=5)

    return qb_df


def clean_flex_df(flex_df):
    """
    Take the single Flex CSV, clean up the column names, add the position and bonus
    columns,END.       XXX get custom score, split into positional DataFrames, and add VBD XXXX
    """

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
    # flex_df["fpts"] = flex_df.apply(self.get_custom_score_row, axis=1)
    # flex_df.sort_values(by="fpts", inplace=True, ascending=False)
    """
    # split into RB, WR, and TE DFs, return all 4
    rb_df = flex_df[flex_df["position"] == "RB"]
    rb_df = self.add_vbd(rb_df)
    wr_df = flex_df[flex_df["position"] == "WR"]
    wr_df = self.add_vbd(wr_df)
    te_df = flex_df[flex_df["position"] == "TE"]
    te_df = self.add_vbd(te_df)
    """

    flex_df.dropna(inplace=True, thresh=5)

    return flex_df


def get_fpros_projections():
    qb_path = Path("data/fpros/FantasyPros_Fantasy_Football_Projections_QB.csv")
    flex_path = Path("data/fpros/FantasyPros_Fantasy_Football_Projections_FLX.csv")

    qb_df = pd.read_csv(qb_path, skiprows=[1])
    flex_df = pd.read_csv(flex_path, skiprows=[1])

    qb_df = clean_qb_df(qb_df)
    qb_df = get_sleeper_ids(qb_df)
    flex_df = clean_flex_df(flex_df)
    flex_df = get_sleeper_ids(flex_df)

    prj_df = pd.concat([qb_df, flex_df]).fillna(0)

    return prj_df


def get_fpros_data(player_count=225):
    ecr_df = get_ecr_rankings(player_count)
    prj_df = get_fpros_projections()
    fpros_df = merge_dfs(ecr_df, prj_df, "sleeper_id")
    return fpros_df


def merge_dfs(df1, df2, col_to_match, how="left"):
    cols_to_use = df2.columns.difference(df1.columns).to_list()
    cols_to_use.append(col_to_match)
    df = pd.merge(df1, df2[cols_to_use], how=how, on=col_to_match)
    return df


# ------------- GUI SETUP and func----------- #
def make_table(gui_df):
    # Table Func for GUI
    table = Table(table_frame, dataframe=gui_df, showtoolbar=True, showstatusbar=True)
    table.autoResizeColumns()
    table.show()


start_time = time.time()
fpros_df = get_fpros_data(player_count=225)
adp_df = get_adp_df()
merge = merge_dfs(fpros_df, adp_df, "sleeper_id", how="outer")
end_time = time.time()
print(f"Time to call ECR Rank AND VBD: {end_time-start_time}")

window = Tk()
window.title("Sleeper Project")
table_frame = Frame(window)
table_frame.pack(fill=BOTH, expand=1, side="right")
select_frame = Frame(window)
select_frame.pack(side="left")
make_table(merge)

window.mainloop()
