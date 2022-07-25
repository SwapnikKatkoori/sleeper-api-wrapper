import pdb
from pathlib import Path
import requests
from sleeper_wrapper import Players
import re
import json
import time
import pandas as pd
from pandastable import Table
from tkinter import *
from datetime import datetime

players = Players()

YEAR = datetime.today().strftime('%Y')
TODAY = datetime.today().strftime('%Y-%m-%d')

def get_search_names(df):
    # ----- Create the search_names (all lowercase, no spaces) ------ #
    search_names = []
    remove = ['jr', 'ii', 'sr']
    for idx, row in df.iterrows():
        if row["team"] == "JAC":
            df.loc[idx, "team"] = "JAX"
        new_name = re.sub(r'\W+', '', row['name']).lower()

        if new_name[-3:] == "iii":
            new_name = new_name[:-3]
        elif new_name[-2:] in remove:
            new_name = new_name[:-2]

        if new_name == "kennethwalker":
            new_name = "kenwalker"
        search_names.append(new_name)

    df['search_full_name'] = search_names
    search_name_tuples = list(zip(df.search_full_name, df.team))

    players_df = players.get_players_df()
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
    return df

def get_adp_df(adp_type="2qb", adp_year=YEAR, teams_count=12, positions="all"):
    start_time = time.time()
    base_url = f"https://fantasyfootballcalculator.com/api/v1/adp/" \
               f"{adp_type}?teams={teams_count}&{adp_year}&position={positions}"
    file_path = Path('data/adp/adp.json')

    try:
        with open(file_path, "r") as data_file:
            adp_data = json.load(data_file)
            adp_end_date = adp_data["meta"]["end_date"]
    except FileNotFoundError:
        adp_end_date = None
        pass

    if adp_end_date == TODAY:
        print(f"Loading local ADP data from {adp_end_date}")
    else:
        print(f"Local ADP data does not match today's date, {TODAY}. Making call to FFCalc.")
        try:
            response = requests.get(base_url)
            adp_data = response.json()
        except requests.exceptions.RequestException as e:
            if adp_end_date:
                print(f"Error {e} when making the remote call.  Using local data from {adp_end_date}")
                pass
            else:
                print("Error reading local copy and error reading remote copy.  Must break. ")
                pass
        finally:
            with open(file_path, 'w') as data_file:
                json.dump(adp_data, data_file, indent=4)


    with open('data/adp/adp.json', 'r') as file:
        adp_data = json.load(file)

    adp_dict = adp_data["players"]

    adp_df = pd.DataFrame(adp_dict)

    adp_df.rename(columns={'player_id': 'ffcalc_id'}, inplace=True)
    adp_df = get_search_names(adp_df)

    end_time = time.time()
    print(end_time - start_time)
    adp_data["players"] = adp_df.to_dict(orient="records")
    with open(file_path, 'w') as data_file:
        json.dump(adp_data, data_file, indent=4)
    return adp_df

def make_table(gui_df):
    """
    Table Func for GUI
    """
    table = Table(table_frame, dataframe=gui_df, showtoolbar=True, showstatusbar=True)
    table.autoResizeColumns()
    table.show()


# ------------- GUI SETUP ----------- #

df = get_adp_df()

window = Tk()
window.title("Sleeper Project")
table_frame = Frame(window)
table_frame.pack(fill=BOTH, expand=1, side="right")
select_frame = Frame(window)
select_frame.pack(side="left")
make_table(df)

window.mainloop()
def get_adp(url="https://fantasyfootballcalculator.com/api/v1/adp/2qb?teams=12&year=2022&position=all"):

    """
    OLD ADP Code
    file_path = Path('data/adp/adp.json')
    try:
        response = requests.get(url)
        adp_data = response.json()
    except requests.exceptions.RequestException as e:
        with open(file_path, "r") as data_file:
            adp_data = json.load(data_file)
    finally:
        adp = adp_data["players"]

    # ---Make the search_full_name value that aligns with Sleeper
    for idx, p in enumerate(adp):
        p["draft_pick"] = idx+1  # add the draft pick = to the index + 1
        p["ffcalc_id"] = p.pop("player_id") # rename the player_id field

        # make the new_name to match the "search_full_name" field
        new_name = (re.sub(r'\W+', '', p["name"]).lower())
        if new_name[-2:] == "jr":
            new_name = new_name[:-2]
        elif new_name[-3:] == "iii":
            new_name = new_name[:-3]
        elif new_name[-2:] == "ii":
            new_name = new_name[:-2]

        if new_name == "kennethwalker":
            new_name = "kenwalker"

        p['search_full_name'] = new_name

        # after adding the search_full_name, search for that value in sleeper
        for k, v in players.items():
            match = False
            try:
                cur_name = v["search_full_name"]
                if p["position"] == "DEF":
                    p["sleeper_id"] = p["team"]
                    pass
                elif cur_name == p["search_full_name"]:
                    if p['team'] == v['team']:
                        p["sleeper_id"] = k
                    else:
                        pass
            except KeyError:
                pass
        if not match:
            print(f"FFCalc: No Match on {new_name} at {adp[idx]}")
    # After doing all of the work on the ADP data, save it to the data folder
    with open(file_path, 'w') as data_file:
        json.dump(adp, data_file, indent=4)

    return adp
    """
    pass
"""
ADP code from db-gui
file_path = Path('data/adp/adp.json')
    pop_count = 0
    try:
        adp_response = requests.get(
            url="https://fantasyfootballcalculator.com/api/v1/adp/2qb?teams=12&year=2022&position=all")
        adp_data = adp_response.json()
        with open(file_path, 'w') as data_file:
            json.dump(adp_data, data_file, indent=4)
    except requests.exceptions.RequestException as e:
        with open(file_path, "r") as data_file:
            adp_data = json.load(data_file)
    finally:
        try:
            adp_list = adp_data['players']
        except:
            pdb.set_trace()
"""