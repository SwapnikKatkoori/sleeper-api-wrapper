from sleeper_wrapper import League, Stats, Drafts, User
import json
import pdb
import pandas as pd
from itertools import chain
from tkinter import *
from pandastable import Table
import requests
import math
from fuzzywuzzy import fuzz, process


def make_table(df):
    table = Table(table_frame, dataframe=df, showtoolbar=True, showstatusbar=True)
    table.autoResizeColumns()
    table.show()





def get_previous_keepers(league):
    prev_league_init = League(league["previous_league_id"])
    prev_league = prev_league_init.get_league()
    prev_draft_id = prev_league['draft_id']
    prev_draft = Drafts(prev_draft_id)
    prev_draft_picks = prev_draft.get_all_picks()
    keeper_list = []

    for pick in prev_draft_picks:
        if pick['is_keeper'] == True:
            keeper_list.append(pick)

    return (keeper_list)



def get_player_name(player_id):
    player_name = str(all_players[player_id]['first_name'] + " " + all_players[player_id]['last_name'])
    return player_name

"""
def get_draft_rounds(player_id):
    player_dict = {}
    player_name = str(all_players[player_id]['first_name'] + " " + all_players[player_id]['last_name'])
    draft_round_2021 = 'Undrafted'
    draft_value_2022 = 16
    team = all_players[player_id]['team']
    position = all_players[player_id]['position']
    keeper = False
    keep_count = 0

    for draft_pick in weez_draft:

        if player_id == draft_pick['player_id']:
            draft_round_2021 = draft_pick['round']
            keeper = draft_pick['is_keeper']

            if keeper == True:
                current_keep_count = 1
                prev_keep_count = check_keeper(player_id, keep_count)
                keep_count = current_keep_count + prev_keep_count

            if draft_pick['round'] < 3:
                draft_value_2022 = 'Cannot Keep (drafted in top 3 rounds)'
            elif keep_count >= 2:
                draft_value_2022 = 'Cannot Keep (kept for 2 consecutive years). '
            else:
                draft_value_2022 = draft_pick['round'] - 2

    player_dict.update(player_name=player_name, position=position, team=team, draft_round_2021=draft_round_2021,
                       draft_value_2022=draft_value_2022, keeper=keeper, keeper_count=keep_count)

    return (player_dict)
"""



def get_keeper_value(row):
    last_year = row["2021 Round"]
    if last_year == "Undrafted":
        return 16
    elif last_year <= 3:
        return "Cannot Keep Player Drafted in First 3 Rounds"
    elif row["2021 On Final Roster"] == \
            row["2020 On Final Roster"] == \
            row["2019 On Final Roster"] == \
            row["2020 Drafted by"] == \
            row["2021 Drafted by"]:
        if row['position'] == "QB":
            return f"Cannot Keep Player more than 2 Consecutive Years. (Round 1 if Traded)"
        else:
            return f"Cannot Keep Player more than 2 Consecutive Years. (Round {last_year - 2} if Traded)"
    else:
        return last_year - 2


def get_all_drafts():
    """
    getting all previous years' keeper and draft round info
    """
    league_id = 850087629952249856
    league = League(league_id)
    all_drafts = []
    all_final_rosters = []
    all_user_maps = []
    while True:
        try:
            prev_league_id = league.previous_league_id
            league = League(prev_league_id)
            all_final_rosters.append(league.rosters_full)
            all_user_maps.append(league.map_users_to_team_name())
            season = league.season
            draft_id = league.draft_id
            current_draft = Drafts(draft_id)
            print(current_draft)
            # pdb.set_trace()
            all_drafts.append(current_draft.get_all_picks())
        except TypeError:
            return all_drafts, all_final_rosters, all_user_maps


def combine_player_info(row):
    # combining these into one field
    return f"{row['first_name']} {row['last_name']}, {row['position']} {row['team']}"

def combine_player_name(row):
    # combining these into one field
    return f"{row['first_name']} {row['last_name']}"

def get_draft_round(row, draft, roster, user_map, season):
    row[f'{season} Round'] = "Undrafted"
    for player in draft:
        if player["player_id"] == row['player_id']:
            row[f'{season} Round'] = player['round']
            row[f'{season} Drafted by'] = user_map[player['picked_by']]
            if player['is_keeper']:
                row[f'{season} Keeper'] = player['is_keeper']

    for r in roster:
        for player in r['player_dicts']:
            if player["player_id"] == row["player_id"]:
                row[f'{season} On Final Roster'] = r['team_name']  # user_map[player['picked_by']]

    return row


def get_adp_round(row):
    return math.ceil(row['adp_rank'] / 12)


def get_adp_df():
    adp_response = requests.get(
        url="https://fantasyfootballcalculator.com/api/v1/adp/2qb?teams=12&year=2022&position=all")
    adp_data = adp_response.json()
    adp_df = pd.DataFrame(adp_data['players'])

    adp_df.rename(columns={'player_id': 'ffcalc_id'}, inplace=True)
    adp_df['adp_rank'] = adp_df.index + 1
    adp_df['average_draft_round'] = adp_df.apply(get_adp_round, axis=1)

    return adp_df


def merge_dfs(df, df2, on="name_stripped"):
    cols_to_use = df2.columns.difference(df.columns)
    df_merged = pd.merge(df, df2[cols_to_use], left_on="matches", right_on="matches", how='outer')
    return df_merged


# initiliaze League - creates new object of League class
# get_league, _rosters, and _users
league_id_2021 = 650057741137690624 # Weez League ID 2021
league_id = 850087629952249856
league = League(league_id)
weez_league = league.get_league() # pulls dict of league
weez_rosters = league.rosters_full
weez_users = league.get_users()
with open('data/players/all_players.json') as json_file:
    all_players = json.load(json_file)

# Grabbing the trimmed roster list
roster_list = league.rosters_trim

# Adding the Weez Owner field to the embedded roster dicts to flatten
for r in roster_list:
    for d in r['roster']:
        d['Weez Owner'] = r['team_name']
roster_list = [d['roster'] for d in roster_list]

# creating a dataframe with itertools
df = pd.DataFrame(list(chain.from_iterable(roster_list)))
pd.set_option('display.max_columns', None)

"""
initialize drafts.  all_drafts is a list, but only 1 item.
other years get different league and draft IDs, found in
weez_league['previous_league_id']
"""
all_drafts = league.get_all_drafts() # this only gets the current draft
weez_draft_id = all_drafts[0]['draft_id']  # 650057741137690625
draft = Drafts(weez_draft_id)
weez_draft = draft.get_all_picks()

# ----- Apply DF funcs and clean up ------ #
df["player"] = df.apply(combine_player_info, axis=1)
df["name"] = df.apply(combine_player_name, axis=1)
df.drop(columns=['first_name', 'last_name'], inplace=True)
df = df[['player_id', 'player', 'position', 'Weez Owner', 'name']]
print(df.head())
all_drafts, all_final_rosters, all_user_maps = get_all_drafts()

# Mapping usernames and final rosters and draft values to the dataframe

season = 2021
for y in range(4):
    df = df.apply(lambda x: get_draft_round(x, all_drafts[y], all_final_rosters[y], all_user_maps[y], season), axis=1)
    season -= 1
    print(y)

# calc 2022 value
df["2022 Keeper Round"] = df.apply(get_keeper_value, axis=1)


cols = df.columns.tolist()
cols.sort(reverse=True)

cols = cols[4:5] + cols[2:3] + cols[5:] + cols[:2] + cols[3:4]
df = df[cols]
# ---------Main DF Complete Here ---------#

"""
Get adp_df and match to DF
"""
adp_df = get_adp_df()


adp_df = get_adp_df()
adp_df_cols = adp_df.columns.tolist()
cols = df.columns.tolist()


def merge_dfs(df, df2, key1, key2):
    cols_to_use = df2.columns.difference(df.columns)
    df_merged = pd.merge(df, df2[cols_to_use], how='outer', left_on=key1, right_on=key2)
    return df_merged


def strip_names(df):
    try:
        df['name_stripped'] = df['name'].str.replace(r'[^\w\s]+', '')
    except KeyError:
        df['name_stripped'] = df['Name'].str.replace(r'[^\w\s]+', '')
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


df, adp_df = strip_names(df), strip_names(adp_df)
df = fuzzy_merge(df, adp_df, "name", "name", 90)

cols_to_use = adp_df.columns.difference(df.columns)
print(cols_to_use)
cols_to_use = cols_to_use.tolist()
cols_to_use.append('name')
try:
    df = pd.merge(df, adp_df[cols_to_use], left_on="matches", right_on="name", how='outer')
except:
    pdb.set_trace()


def get_keeper_value(row):
    try:
        return row['2022 Keeper Round'] - row['average_draft_round']
    except TypeError:
        pass
# pdb.set_trace()


df['2022 Keeper Value'] = df.apply(get_keeper_value, axis=1)


"""
save df to excel
"""
df.to_excel("data/keepers/keeper_values_2022v2.xlsx")
# ------------- GUI SETUP ----------- #
window = Tk()
window.title("Sleeper Project")
table_frame = Frame(window)
table_frame.pack(fill=BOTH, expand=1, side="right")
select_frame = Frame(window)
select_frame.pack(side="left")
make_table(df)

window.mainloop()


