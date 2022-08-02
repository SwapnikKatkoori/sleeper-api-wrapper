from draftboard_brain import *
import pdb
import PySimpleGUI as sg
from pathlib import Path
import json
from sleeper_wrapper import League

"""
Select the League
Display League Info
Calculate Custom Score 

"""
def LeaguePopUp():

    id_path = Path('data/league_ids')
    id_json = Path('data/league_ids/leagues.json')
    try:
        with open(id_json, "r") as file:
            league_id_list = json.load(file)
            league_id_list = list(set(league_id_list))
    except FileNotFoundError:
        id_path.mkdir(parents=True, exist_ok=True)
        league_id_list = [" "]

    col1_layout = [[sg.DropDown(values=league_id_list,
                                default_value=league_id_list[0],
                                size=(20, 1),
                                key='-LEAGUE-ID-DROP-')],
              [sg.Button("Load", enable_events=True, key="-LOAD-LEAGUE-")],
              [sg.Text("League Info")]]
    col1 = sg.Column(col1_layout)
    col2_layout = [[sg.Text("League Info")], ] # [sg.Table(values=[], key="-LEAGUE-TABLE-")]]
    col2 = sg.Column(col2_layout, key="-COL2-",)
    layout = [[col1] + [sg.VerticalSeparator()] + [col2]]
    window = sg.Window("League", layout=layout, size=(800, 600))
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            # save_keepers(df.loc[df["is_keeper"] == True].to_dict('records'))
            break
        elif event == "-LOAD-LEAGUE-":
            # pdb.set_trace()
            l_id = int(window["-LEAGUE-ID-DROP-"].get())

            try:
                league = League(league_id=l_id)
                league_id_list.append(window["-LEAGUE-ID-DROP-"].get())
                with open(id_json, "w") as file:
                    json.dump(league_id_list, file, indent=4)
                window["-LEAGUE-ID-DROP-"].update(values=list(set(league_id_list)))
                league_info = league.get_league()

                sg.Popup(f"League {league_info['name']} loaded.\n")
                with open(f'data/league_ids/{l_id}.json', "w") as file:
                    json.dump(league_info, file, indent=4)
                return league
            except TypeError:
                sg.popup_quick_message("Sorry, that is not a valid league ID")

    window.close()


# LeaguePopUp()
