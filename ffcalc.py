import pdb
from pathlib import Path
import requests
from sleeper_wrapper import Players
import re
import json

players = Players()
players = players.get_all_players()

def get_adp(url="https://fantasyfootballcalculator.com/api/v1/adp/2qb?teams=12&year=2022&position=all"):

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
        p["draft_pick"] = idx+1
        p['search_full_name'] = (re.sub(r'\W+', '', p["name"]).lower())
        if p['search_full_name'][:-2] == "jr":
            p['search_full_name'] = p['search_full_name'][:-2]
            pdb.set_trace()
        if p['position'] == "PK":
            p['position'] = "K"

    for k, v in players.items():
        try:
            cur_name = v["search_full_name"]
            for p in adp:
                if "sleeper_id" in p.keys():
                    pass
                elif p["position"] == "DEF":
                    p["sleeper_id"] = p["team"]
                elif cur_name == "cordarrellepatterson":
                    p["sleeper_id"] = k
                elif cur_name[:10] == p["search_full_name"][:10]:
                    if p['team'] == v['team']:
                        if p["position"] in v["fantasy_positions"]:
                            p["sleeper_id"] = k
                        else:
                            print(f"failure on {p} in adp\n {v} in sleeper")
        except KeyError:
            pass

    # After doing all of the work on the ADP data, save it to the data folder
    with open(file_path, 'w') as data_file:
        json.dump(adp, data_file, indent=4)

    return adp

adp = get_adp()

print(adp)

