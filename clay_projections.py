import pdb
from pathlib import Path
import pandas as pd
from sleeper_wrapper import League, Drafts
from tkinter import *
from tkinter import ttk
from pandastable import Table, TableModel, config
import json
import requests
from fuzzywuzzy import fuzz, process
import math
POS_LIST = ['QB', 'RB', 'WR', 'TE']
LEAGUE_ID = 850087629952249856


def make_table(df):
    table = Table(table_frame, dataframe=df, showtoolbar=True, showstatusbar=True)
    table.autoResizeColumns()
    table.show()


def get_fantasy_points(row):
    # g = row['G']  # access the G column
    score = 0
    for k, v in scoring.items():
        try:
            score += scoring[k] * row[k]
            # print(f"success key: {k}, value: {v}, score: {scoring[k] * row[k]}")
        except KeyError:
            pass
            # print(f"error: {k}")
    # pdb.set_trace()
    return round(score)


def print_scoring_kv():
    for k, v in scoring.items():
        print(k, v)


def calc_vols(row):
    if row['Pos'] == 'QB':
        vols_threshold = qb_df.iloc[25]['FF_Pt']
    elif row['Pos'] == 'RB':
        vols_threshold = rb_df.iloc[33]['FF_Pt']
    elif row['Pos'] == 'WR':
        vols_threshold = wr_df.iloc[33]['FF_Pt']
    elif row['Pos'] == 'TE':
        vols_threshold = te_df.iloc[13]['FF_Pt']
    else:
        pass

    return max(0, row['FF_Pt'] - vols_threshold)


def calc_vorp(row):
    if row['Pos'] == 'QB':
        vorp_threshold = qb_df.iloc[33]['FF_Pt']
    elif row['Pos'] == 'RB':
        vorp_threshold = rb_df.iloc[63]['FF_Pt']
    elif row['Pos'] == 'WR':
        vorp_threshold = wr_df.iloc[63]['FF_Pt']
    elif row['Pos'] == 'TE':
        vorp_threshold = te_df.iloc[17]['FF_Pt']
    else:
        pass

    return max(0, row['FF_Pt'] - vorp_threshold)


def calc_vbd(row):
    return max(0, row['vols'] + row['vorp'])


def add_vbd(df):
    df['FF_Pt'] = df.apply(get_fantasy_points, axis=1)
    df.sort_values(by="FF_Pt", ascending=False, inplace=True)
    df['vols'] = df.apply(calc_vols, axis=1)
    df['vorp'] = df.apply(calc_vorp, axis=1)
    df['vona'] = df.FF_Pt.diff(periods=-1)
    df['vbd'] = df.apply(calc_vbd, axis=1)
    cols = df.columns.tolist()
    cols = cols[:6] + cols[-4:] + cols[7:-4]
    df = df[cols]
    return df


def cleanup_qb_df(df):
    df.rename(columns={'Quarterback': 'Name', 'Pos Rk FF Pt': 'Pos_Rk', 'Unnamed: 4': 'FF_Pt'}, inplace=True)
    df.rename(columns={'INT': 'pass_int'}, inplace=True)
    df.rename(columns={'Ru Yds': 'rush_yd', 'Ru TD': 'rush_td', 'P TD': 'pass_td', 'P Yds': 'pass_yd'}, inplace=True)
    df = add_vbd(df)
    return df


def cleanup_wr_df(df):
    df.rename(columns={' FF Pt': 'FF_Pt', 'Ru Yds ': 'rush_yd', 'Ru TD': 'rush_td'}, inplace=True)
    df.rename(columns={'INT': 'pass_int', ' Targ': 'Targ'}, inplace=True)
    df.rename(columns={'Pos Rk': 'Pos_Rk'}, inplace=True)
    df.rename(columns={'Re Yd': 'rec_yd', 'Re TD': 'rec_td', 'Rec': 'rec', 'P Yds': 'pass_yd'}, inplace=True)
    df = add_vbd(df)
    return df


def cleanup_rb_df(df):
    df.rename(columns={' FF Pt': 'FF_Pt', 'Ru Yds ': 'rush_yd', 'Ru TD': 'rush_td'}, inplace=True)
    df.rename(columns={'INT': 'pass_int'}, inplace=True)
    df.rename(columns={'Pos Rk': 'Pos_Rk'}, inplace=True)
    df.rename(columns={'POS': 'Pos'}, inplace=True)
    df.rename(columns={'Carry Ru Yds Ru TD Targ': 'Carry'}, inplace=True)
    df.rename(columns={'Unnamed: 7': 'rush_yd', 'Unnamed: 8': 'rush_td', 'Unnamed: 9': 'Targ'}, inplace=True)
    df.rename(columns={'Re Yd': 'rec_yd', 'Re TD': 'rec_td', 'Rec': 'rec', 'P Yds': 'pass_yd'}, inplace=True)
    df = add_vbd(df)
    return df


def cleanup_te_df(df):
    df.rename(columns={' FF Pt': 'FF_Pt', ' Ru Yds': 'rush_yd', ' Ru TD': 'rush_td'}, inplace=True)
    df.rename(columns={'Pos Rk': 'Pos_Rk'}, inplace=True)
    df.rename(columns={'POS': 'Pos', 'target': 'Targ'}, inplace=True)
    df.rename(columns={'Re Yd': 'rec_yd', 'Re TD': 'rec_td', 'Rec': 'rec', 'P Yds': 'pass_yd'}, inplace=True)
    df['bonus_rec_te'] = df['rec']
    df = add_vbd(df)
    return df


def fuzzy_merge(df_1, df_2, key1, key2, threshold=90, limit=2):
    """
    :param df_1: the left table to join
    :param df_2: the right table to join
    :param key1: key column of the left table
    :param key2: key column of the right table
    :param threshold: how close the matches should be to return a match, based on Levenshtein distance
    :param limit: the amount of matches that will get returned, these are sorted high to low
    :return: dataframe with both keys and matches
    """
    s = df_2[key2].tolist()

    m = df_1[key1].apply(lambda x: process.extract(x, s, limit=limit))
    df_1['matches'] = m

    m2 = df_1['matches'].apply(lambda x: ', '.join([i[0] for i in x if i[1] >= threshold]))
    df_1['matches'] = m2

    return df_1


def get_adp_round(row):
    return math.ceil(row['adp_rank'] / 12)


def strip_names(df):
    df['Name'] = df['Name'].str.replace(r'[^\w\s]+', '')
    return df


def get_keeper_values():
    keeper_path = Path("data/keepers/keeper_values_2022.xlsx")
    df = pd.read_excel(io=keeper_path)
    df['player_name'] = df['player_name'].str.replace(r'[^\w\s]+', '')
    return df


def adp_keeper_round_diff(row):
    try:
        return int(row["draft_value_2022"]) - row["adp_round"]
    except ValueError:
        pass


def vbd_expected_vbd_diff(row):
    return row["vorp"] - row["Expected Value"]


league = League(LEAGUE_ID)
scoring = league.scoring_settings
rosters = league.get_rosters()
list_rosters_df = [pd.DataFrame(rosters[x].roster).melt() for x in range(12)]
rosters_df = pd.concat(list_rosters_df)
rosters_df.rename(columns={'variable': 'weez_team', 'value': 'Name'}, inplace=True)
rosters_df = strip_names(rosters_df)


file_path = Path("data/projections/NFLDK2022_CS_ClayProjections2022.xlsx")
wr_df = pd.read_excel(io=file_path, sheet_name="WR")
wr_df = cleanup_wr_df(wr_df)
qb_df = pd.read_excel(io=file_path, sheet_name="QB")
qb_df = cleanup_qb_df(qb_df)
rb_df = pd.read_excel(io=file_path, sheet_name="RB")
rb_df = cleanup_rb_df(rb_df)
te_df = pd.read_excel(io=file_path, sheet_name="TE")
te_df = cleanup_te_df(te_df)

frames = [qb_df, wr_df, rb_df, te_df]
all_df = pd.concat(frames)
all_df = strip_names(all_df)
all_df.sort_values(by="vbd", ascending=False, inplace=True)
# print(result.head(15))

adp_response = requests.get(url="https://fantasyfootballcalculator.com/api/v1/adp/2qb?teams=12&year=2022&position=all")
adp_data = adp_response.json()
adp_df = pd.DataFrame(adp_data['players'])
adp_df.rename(columns={'name': 'Name', 'position': 'Pos', 'team': 'Team'}, inplace=True)
adp_df = strip_names(adp_df)
adp_df['adp_rank'] = adp_df.index+1
# Match up expected VBD from Excel - TODO Need to add code from previous exercise
adp_value_path = Path("data/adp/draft_value_chart.xlsx")
adp_value_df = pd.read_excel(io=adp_value_path)
adp_df = pd.merge(adp_df, adp_value_df, left_on="adp_rank", right_on="Pick", how="left")
adp_df['adp_round'] = adp_df.apply(get_adp_round, axis=1)

all_df.sort_values(by="vbd", ascending=False, inplace=True)
all_df = all_df.reset_index(drop=True)
all_df['vbd_rank'] = all_df.index+1  # .rank(method='first', ascending=False)

all_df = fuzzy_merge(all_df, adp_df, "Name", "Name", 90)
all_df = pd.merge(all_df, adp_df, left_on='matches', right_on='Name', how='left')
all_df.rename(columns={"Name_x": "Name"}, inplace=True)
all_df = fuzzy_merge(all_df, rosters_df, "Name", "Name", 90)
all_df = pd.merge(all_df, rosters_df, left_on='matches', right_on='Name', how='left')
all_df.sort_values(by="adp_rank", ascending=True, inplace=True)
all_df = all_df.reset_index(drop=True)
all_df['adp_rank'] = all_df.index+1  # .rank(method='first', ascending=False)
all_df['vbd_adp_diff'] = all_df['vbd_rank'] - all_df['adp_rank']


keeper_df = get_keeper_values()
all_df = pd.merge(all_df, keeper_df, left_on='matches', right_on='player_name', how='left')

all_df["ADP - Keeper Round"] = all_df.apply(adp_keeper_round_diff, axis=1)
all_df["VBD - Expected VBD"] = all_df.apply(vbd_expected_vbd_diff, axis=1)
# cols = all_df.columns.tolist()
# cols = cols[-2:] + cols[0:11]  # + cols[7:-4]
# all_df = all_df[cols]
# cols = cols[-1:] + cols[0:11]

# Draft/Keeper Round


# Get the Expected VBD/Rounds


# average the expected VBD/Rounds





# ------------- GUI SETUP ----------- #
window = Tk()
window.title("Sleeper Project")
table_frame = Frame(window)
table_frame.pack(fill=BOTH, expand=1, side="right")
select_frame = Frame(window)
select_frame.pack(side="left")
make_table(all_df)

window.mainloop()
