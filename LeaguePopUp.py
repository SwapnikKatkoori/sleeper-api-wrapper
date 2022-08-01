from draftboard_brain import *
import pdb
import PySimpleGUI as sg
from pathlib import Path
import json
def LeaguePopUp():
    league_id_path = Path('data/league_ids/league_ids.json')
    try:
        with open(league_id_path, "r") as file:
            league_id_list = json.load(file)
    except FileNotFoundError:
        league_id_list = []
    values = [i for i in range(15)]
    layout = [[sg.DropDown(size=(20, 1), values=league_id_list, key='SELECT-LEAGUE')],
              [sg.Button("Select", enable_events=True)]]
    window = sg.Window("League", layout=layout, size=(800,600))
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            # save_keepers(df.loc[df["is_keeper"] == True].to_dict('records'))
            break
        elif event == "Select":
            sg.popup_quick_message("Hi")
    window.close()

LeaguePopUp()
