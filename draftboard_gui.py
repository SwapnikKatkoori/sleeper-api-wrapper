#!/usr/bin/env python
import pdb
import PySimpleGUI as sg
import csv
import requests
import numpy as np



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
                 "PK": "lavender",
                 "DEF": "sienna",
                 ".": "white"}

    """
    Get ADP Data and list of players, add empty items in the list with for loop to convert  to NP array
    """
    adp_response = requests.get(
        url="https://fantasyfootballcalculator.com/api/v1/adp/2qb?teams=12&year=2022&position=all")
    adp_data = adp_response.json()
    adp_list = adp_data['players']
    adp_list_length = len(adp_list)
    if len(adp_list) > 192:
        for x in range(adp_list_length - BOARD_LENGTH):
            print(f"Removing item: {adp_list.pop(-1)}")
    elif len(adp_list) < 192:
        for x in range(BOARD_LENGTH - adp_list_length):
            adp_list.append({"name": "", "position": ".", "team": ""})
    adp = np.array(adp_list)
    adp = np.reshape(adp, (16, 12))
    adp[1::2, :] = adp[1::2, ::-1]


    column_layout = [[sg.Text(f"Rd {str(r+1)}:", size=(5, 1), justification='left')] +
                     [sg.Text(
                         text=f"{adp[r, c]['name']}\n{adp[r,c]['position']}",
                         size=(10,4),
                         justification="left",
                         border_width=1,
                         relief=RELIEF_,
                         enable_events=True,
                         background_color=BG_COLORS[adp[r,c]["position"]],
                         # button_color=BG_COLORS[adp[r,c]["position"]],
                         # disabled_button_color="grey",
                         key=(r, c)) for c in range(MAX_COL)]
                     for r in range(MAX_ROWS)]

    layout = [[sg.Menu(menu_def)],
              [sg.Text('Weez Draftboard', font='Any 18')],
              [sg.Col(column_layout, size=(800, 796), scrollable=True)]]

    window = sg.Window('Table', layout,  return_keyboard_events=True)

    while True:
        event, values = window.read()

        # --- Process buttons --- #
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        elif event in [(r, c) for c in range(MAX_COL) for r in range(MAX_ROWS)]:
            r, c = event

            # pdb.set_trace()
            if 'gray' not in window[(r, c)].BackgroundColor:
                window[(r, c)].update(background_color='gray')
            else:
                window[(r, c)].update(background_color=BG_COLORS[adp[r, c]["position"]])

    """
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



        # if a valid table location entered, change that location's value
        try:
            location = (int(values['inputrow']), int(values['inputcol']))
            target_element = window[location]
            new_value = values['value']
            if target_element is not None and new_value != '':
                target_element.update(new_value)
        except:
            pass
    """
    window.close()


TableSimulation()