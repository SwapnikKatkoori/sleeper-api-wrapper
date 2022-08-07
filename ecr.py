import pdb
import re
import pandas as pd
from pathlib import Path
import time
from pandastable import Table
from tkinter import *
from ffcalc import get_sleeper_ids, get_adp_df
import json
import PySimpleGUI as sg
import numpy as np
MAX_ROWS = 17
MAX_COLS = 12


def get_cheatsheet_list(df, pos):
    df = df[df["position"] == pos]  #  ['position_tier_ecr', 'cheatsheet_text'].tolist()
    df = df[["position_tier_ecr", 'cheatsheet_text']]
    """
    scratch Cheat Sheet List Building
    # rb_list = PP[PP["position"] == "RB"].sort_values(by="position_rank_ecr").to_dict("records")
    rb_list = PP[PP["position"] == "RB"].groupby('position_tier_ecr')['cheatsheet_text'].apply(list)
    rb_list = [r for r in rb_list]
    for idx, x in enumerate(rb_list):
        print(idx, x)
    # r_list = [[f"{idx+1} {p}" for p in player] for idx, player in enumerate(r_list)]
    new_list = [sublist for sublist in rb_list]

    # df = df.T
    # df = df.groupby(by='position_tier_ecr', level=1)
    # df = PP[[PP["position"] == "RB"], "position_tier_ecr", "cheatsheet_text"]
    # df.reset
    # df.sort_values(by=['position_tier_ecr'], ascending=True, inplace=True, na_position='last')
    # ecr_cheat=PP.sort_values(by=['superflex_rank_ecr'], ascending=True, na_position='last')
    # pdb.set_trace()
    """
    return df.values.tolist()


def get_db_arr(df, key):
    keys = {"adp": {"sort": "adp_pick", "pick_no": "adp_pick_no"},
            "ecr": {"sort": "superflex_rank_ecr", "pick_no": 'ecr_pick_no'},
            "empty": {"sort": "", "pick_no": ""}
            }
    if key in ["adp", "ecr"]:
        sort = keys[key]['sort']
        pick_no = keys[key]['pick_no']
        non_kept_picks = [n + 1 for n in range(len(df)) if n + 1 not in df['pick_no'].to_list()]
        df[pick_no] = df["pick_no"]
        df.sort_values(by=sort, ascending=True, inplace=True)
        df.loc[df["is_keeper"] != True, f'{key}_pick_no'] = non_kept_picks
        df.sort_values(by=pick_no, ascending=True, inplace=True)
        arr = np.array(df[:MAX_ROWS * MAX_COLS].to_dict("records"))
        arr = np.reshape(arr, (MAX_ROWS, MAX_COLS))
        arr[1::2, :] = arr[1::2, ::-1]
    elif key == "empty":
        arr = np.empty([MAX_ROWS, MAX_COLS])
        arr = np.reshape(arr, (MAX_ROWS, MAX_COLS))
        arr[1::2, :] = arr[1::2, ::-1]
        arr = np.full((MAX_ROWS, MAX_COLS), {"button_text": "\n\n", "position": "-"})
    return arr


def DraftIdPopUp():
    sg.PopupScrolled('Select Draft ID')
    pass


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

def get_ecr_cs(df, hide_drafted=False ):
    """
    Cheat Sheet List building
    """
    ecr_cols = ['sleeper_id', 'superflex_tier_ecr', 'name', 'team', 'position', 'superflex_rank_ecr', ]
    if hide_drafted:
        df2 = df.loc[df['is_drafted'] != True]
        ecr_cheat = df2.sort_values(by=['superflex_rank_ecr'], ascending=True, na_position='last')
    else:
        ecr_cheat = df.sort_values(by=['superflex_rank_ecr'], ascending=True, na_position='last')
    ecr_cheat = ecr_cheat[ecr_cols]
    ecr_cheat.fillna(value="-", inplace=True)
    ecr_data = ecr_cheat.values.tolist()
    return ecr_data


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


def get_player_pool(player_count=400):
    start_time = time.time()
    fpros_df = get_fpros_data(player_count)
    adp_df = get_adp_df()

    # remove kickers and defenses
    adp_kd = adp_df.loc[adp_df['position'].isin(["PK", "DEF"])]

    # Fix Defensive Names
    adp_kd.loc[adp_kd["position"] == "DEF", "last_name"] = adp_kd.name.str.split(' ').str[-1]
    adp_kd.loc[adp_kd["position"] == "DEF", "first_name"] = adp_kd.name.str.replace(' Defense', '')

    # Get ADP DF of only position groups
    adp_df = adp_df.loc[adp_df['position'].isin(["QB", "WR", "TE", "RB"])]
    # merge adp w/out K and D to the fpros dataframe
    p_pool = merge_dfs(fpros_df, adp_df, "sleeper_id", how="outer")
    # Now merge kickers and defenses back in
    p_pool = pd.concat([p_pool, adp_kd])

    # Now time to clean up some ranking columns
    p_pool.sort_values(by=['adp_pick', 'superflex_rank_ecr'], na_position='last', inplace=True)
    p_pool.reset_index(drop=True, inplace=True)
    p_pool['adp_pick'] = p_pool.index + 1

    p_pool[['superflex_rank_ecr', 'superflex_tier_ecr']] = p_pool[
        ['superflex_rank_ecr', 'superflex_tier_ecr']].fillna(
        value=999).astype(int)

    p_pool['team'] = p_pool['team'].fillna("FA")
    p_pool['pos_rank'] = p_pool["pos_rank"].fillna("NA999")

    # Now time to add the button_text and cheatsheet_text values
    p_pool["cheatsheet_text"] = p_pool['pos_rank'] + ' ' + p_pool['name'] + ' ' + p_pool['team']
    p_pool["button_text"] = p_pool['first_name'] + '\n' + p_pool['last_name'] + '\n' + p_pool[
        'position'] + ' (' + p_pool['team'] + ') ' + p_pool['bye'].astype(str)


    # Add in None values for Keeper columns
    # board_loc will eventually be the tuple that can be used to place on the draftboard array
    k_cols = ['is_keeper', 'is_drafted', 'pick_no', 'draft_slot', 'round', 'board_loc']

    for k in k_cols:
        if k in ['is_keeper', 'is_drafted']:
            p_pool[k] = False
        else:
            p_pool[k] = None


    # Open keeper list of dicts so that we can set the keeper value to True
    keeper_list = open_keepers(get="list")

    # iterate over the keeper list to grab the dict values and assign to the main player_pool dataframe
    for p in keeper_list:
        if 'player_id' in p.keys():
            p['sleeper_id'] = p['player_id']
        id = p['sleeper_id']
        is_keeper = p['is_keeper']
        # initializing the keeper/drafted value as them same.  The values will update while drafting
        is_drafted = p['is_keeper']
        pick_no = p['pick_no']
        slot = p['draft_slot']
        rd = p['round']
        board_loc = "hi"
        try:
            p_pool.loc[p_pool['sleeper_id'] == id, k_cols] = [is_keeper, is_drafted, pick_no, slot, rd, board_loc]
        except:
            print(board_loc)
            pdb.set_trace()
    # now add the adp_k_pick column
    # p_pool.sort_values(by=['adp_pick'], ascending=True, inplace=True)

    p_pool.dropna(subset=["name", "button_text"], inplace=True)

    # MOCK - 855693188285992960; 858792885288538112; 858793089177886720
    end_time = time.time()
    print(f"Time to make Player Draft Pool: {end_time - start_time}")
    return p_pool


def reorder_keepers(key, p_pool):
    p_pool.sort_values(by=[key], ascending=True, inplace=True)
    return


def open_keepers(get=None):
    """
    This func checks for the keepers saved in keepers.json
    get="text" returns just the round/slot and sleeper id as list of dicts
    get="list" returns the list of full dicts
    """
    keeper_json_path = Path('data/keepers/keepers.json')
    try:
        with open(keeper_json_path, "r") as data:
            keeper_list = json.load(data)
            # pdb.set_trace()
            print(f"Opened Keeper List: {keeper_list}")
            keeper_list_text = [f"{k['round']}.{k['draft_slot']} {k['sleeper_id']}" for k in keeper_list]
    except KeyError:
        with open(keeper_json_path, "r") as data:
            keeper_list = json.load(data)
            # pdb.set_trace()
            print(f"Opened Keeper List: {keeper_list}")
            keeper_list_text = [f"{k['round']}.{k['draft_slot']} {k['player_id']}" for k in keeper_list]
    except FileNotFoundError:
        keeper_list = []
        keeper_list_text = []

    if not get:
        return keeper_list, keeper_list_text
    elif get == "list":
        return keeper_list
    elif get == "text":
        return keeper_list_text
    else:
        print("Can only accept 'list' or 'text'")
        return None


def clear_all_keepers():
    keeper_list = []
    with open('data/keepers/keepers.json', 'w') as file:
        json.dump(keeper_list, file, indent=4)
    print("keepers.json overwritten, set as []")







# ------------- GUI SETUP and func----------- #
def make_table(gui_df):
    # Table Func for GUI
    table = Table(table_frame, dataframe=gui_df, showtoolbar=True, showstatusbar=True)
    table.autoResizeColumns()
    table.show()

# clear_all_keepers()
"""
draft_pool = get_player_pool()
window = Tk()
window.title("Sleeper Project")
table_frame = Frame(window)
table_frame.pack(fill=BOTH, expand=1, side="right")
select_frame = Frame(window)
select_frame.pack(side="left")
make_table(draft_pool)

window.mainloop()

"""
