#!/usr/bin/env python
import pdb
import PySimpleGUI as sg
import csv
import requests
import numpy as np
from pathlib import Path
import json


def cell_clicked(event):
    print("you clicked me")


def TableSimulation():
    """
    Display data in a table format
    """

    sg.popup_quick_message('Hang on for a moment, this will take a bit to create....', auto_close=True, non_blocking=True, font='Default 18')

    sg.set_options(element_padding=(0, 0))

    menu_def = [['File', ['Open', 'Save', 'Exit']],
                ['Edit', ['Paste', ['Special', 'Normal', ], 'Undo'], ],
                ['Help', 'About...'], ]

    MAX_ROWS = 16
    MAX_COL = 12
    BOARD_LENGTH = MAX_ROWS*MAX_COL
    RELIEF_ = "solid"  # "groove" "raised" "sunken" "flat" "ridge"
    BG_COLORS = {"WR": "DodgerBlue",
                 "QB": "DeepPink",
                 "RB": "LimeGreen",
                 "TE": "coral",
                 "PK": "purple",
                 "DEF": "sienna",
                 ".": "white"}

    """
    Get ADP Data and list of players, add empty items in the list with for loop to convert  to NP array
    """
    file_path = Path('data/adp/adp.json')
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
        draft_list = adp_data['players']
    adp_list_length = len(draft_list)
    if len(draft_list) > 192:
        for x in range(adp_list_length - BOARD_LENGTH):
            print(f"Removing item: {draft_list.pop(-1)}")
    elif len(draft_list) < 192:
        for x in range(BOARD_LENGTH - adp_list_length):
            draft_list.append({"name": "", "position": ".", "team": ""})

    """
    Create draftboard (db) from numpy array of draft_list
    """
    db = np.array(draft_list)
    db = np.reshape(db, (16, 12))
    db[1::2, :] = db[1::2, ::-1]

    """
    Create JSON to store/read keepers
    """

    """
    TODO: Map and create right-click menus,
    Sort by ADP or VBD or VOLS or VORP
    Create Keeper method
    """

    # noinspection PyTypeChecker
    column_layout = [[sg.Text(f"Rd {str(r+1)}:", size=(5, 1), justification='left')] +
                     [sg.B(
                         button_text=
                         f"{db[r, c]['name'].split(' ', 1)[0]}\n"
                         f"{db[r, c]['name'].split(' ', 1)[1]}\n"
                         f"{db[r,c]['position']} ({db[r, c]['team']}) {db[r, c]['bye']}",
                         enable_events=True,
                         size=(14, 0),
                         p=(0, 0),
                         border_width=1,
                         button_color=BG_COLORS[db[r,c]["position"]],
                         mouseover_colors="gray",
                         highlight_colors=("black", "white"),
                         disabled=False,
                         disabled_button_color=(None, "gray"),
                         auto_size_button=False,
                         key=(r, c)
                     )
                         for c in range(MAX_COL)] for r in range(MAX_ROWS)]

    layout = [[sg.Menu(menu_def)],
              [sg.Text('Weez Draftboard', font='Any 18'),
                sg.Combo(
                   values=[x['name'] for x in draft_list],
                   default_value=draft_list[0]['name'],
                   readonly=False,
                   size=(14, 10),
                   enable_events=True,
                   k='Keeper Combo'),
               sg.Text('Round'),
               sg.Combo(values=[x+1 for x in range(16)]),
               sg.Text('Pick'),
               sg.Combo(values=[x + 1 for x in range(12)]),
               sg.Button('Set Keeper')],
              [sg.Col(column_layout, size=(1200, 796), scrollable=True)]]

    window = sg.Window('Table', layout,  return_keyboard_events=True)

    while True:
        event, values = window.read()

        # --- Process buttons --- #
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        elif event in [(r, c) for c in range(MAX_COL) for r in range(MAX_ROWS)]:
            r, c = event
            if 'gray' not in window[(r, c)].ButtonColor:
                window[(r, c)].update(button_color='gray')
            else:
                window[(r, c)].update(button_color=BG_COLORS[db[r, c]["position"]])


        elif event == 'About...':
            sg.popup('Demo of table capabilities')
        elif event == 'Open':
            filename = sg.popup_get_file(
                'filename to open', no_window=True, file_types=(("CSV Files", "*.csv"),))
            # --- populate table with file contents --- #
            if filename is not None:
                with open(filename, "r") as infile:
                    reader = csv.reader(infile)
                    try:
                        # read everything else into a list of rows
                        data = list(reader)
                    except:
                        sg.popup_error('Error reading file')
                        continue
                # clear the table
                [window[(i, j)].update('') for j in range(MAX_COL)
                 for i in range(MAX_ROWS)]

                for i, row in enumerate(data):
                    for j, item in enumerate(row):
                        location = (i, j)
                        try:            # try the best we can at reading and filling the table
                            target_element = window[location]
                            new_value = item
                            if target_element is not None and new_value != '':
                                target_element.update(new_value)
                        except:
                            pass
        elif event == "Set Keeper":
            # if a valid table location entered, change that location's value
            try:
                player_name = window['Keeper Combo'].get()
                pdb.set_trace()
                location = (int(values['inputrow']), int(values['inputcol']))
                target_element = window[location]
                new_value = values['value']
                if target_element is not None and new_value != '':
                    target_element.update(new_value)
            except:
                pass

    window.close()


TableSimulation()