from draftboard_brain import *
import pdb
import PySimpleGUI as sg
from pathlib import Path
import json
from sleeper_wrapper import League
def LeaguePopUp():
    id_path = Path('data/league_ids')
    id_json = Path('data/league_ids/leagues.json')
    try:
        with open(id_json, "r") as file:
            league_id_list = json.load(file)
    except FileNotFoundError:
        id_path.mkdir(parents=True, exist_ok=True)
        league_id_list = []
    values = [i for i in range(15)]
    layout = [[sg.DropDown(size=(20, 1), values=league_id_list, key='-LEAGUE-ID-')],
              [sg.Button("Load", enable_events=True, key="-LOAD-LEAGUE-")]]
    window = sg.Window("League", layout=layout, size=(800, 600))
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            # save_keepers(df.loc[df["is_keeper"] == True].to_dict('records'))

            break
        elif event == "-LOAD-LEAGUE-":
            # pdb.set_trace()
            l_id = window["-LEAGUE-ID-"].get()
            print(l_id)
            try:
                league = League(league_id=l_id)
                with open(id_json, "w") as file:
                    json.dump(window["-LEAGUE-ID-"].get(), file, indent=4)
                print(league.settings)
            except TypeError:
                sg.popup_quick_message("Sorry, that is not a valid league ID")

    window.close()


LeaguePopUp()
