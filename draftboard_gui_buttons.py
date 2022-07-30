"""
Roadmap:


# ----- What do we want the player objects to look like? ------- #
 1. How does it come from Sleeper Draft, Sleeper Players
    a. Sleeper Draft List:
     This List is constantly refreshing from the draft board.
        [{'round': 1,
        'roster_id': None,
        'player_id': '6813',
        'picked_by': '',
        'pick_no': 1,
        'is_keeper': None,
        'draft_slot': 1,
        'draft_id': '856772332067360768'},
        'metadata': {'years_exp': '2', 'team': 'IND', 'status': 'Active', 'sport': 'nfl', 'position': 'RB',
                    'player_id': '6813', 'number': '28', 'news_updated': '1641768012609', 'last_name': 'Taylor',
                    'injury_status': '', 'first_name': 'Jonathan'}
        ... ]

    b. Sleeper Players:
        46 Columns: Perhaps all in the meta-data fields?

 2. How does it come from FF Calc ADP:
    [{
        "name": "Jonathan Taylor",
        "position": "RB",
        "team": "IND",
        "adp": 1.3,
        "adp_formatted": "1.01",
        "times_drafted": 261,
        "high": 1,
        "low": 3,
        "stdev": 0.5,
        "bye": 14,
        "draft_pick": 1,
        "ffcalc_id": 4864,
        "search_full_name": "jonathantaylor",
        "sleeper_id": "6813"
    },

 3. How does it come from Fantasy Pros.
    [{
        "name": "Josh Allen",
        "team": "BUF",
        "pass_att": 607.7,
        "cmp": 389.0,
        "pass_yd": 4334.3,
        "pass_td": 34.9,
        "pass_int": 14.5,
        "rush_att": 120.0,
        "rush_yd": 670.1,
        "rush_td": 6.9,
        "fum_lost": 3.8,
        "fpts": 392.38199999999995,
        "position_rank_projections": 1,
        "position": "QB",
        "vols": 153.51199999999997,
        "vorp": 270.55799999999994,
        "vbd": 424.06999999999994,
        "vona": 31.925999999999988,
        "position_rank_vbd": 1,
        "pos_rank": "QB1",
        "rec": 0.0,
        "rec_yd": 0.0,
        "rec_td": 0.0,
        "bonus_rec_te": 0.0,
        "overall_vbd_rank": 1,
        "superflex_rank_ecr": 1.0,
        "superflex_tier_ecr": 1.0,
        "bye": "7",
        "sos_season": "3 out of 5 stars",
        "ecr_vs_adp": "0",
        "position_rank_ecr": 1.0,
        "position_tier_ecr": 1.0,
        "search_full_name": "joshallen",
        "sleeper_id": "4984"
    },

 4. Player Objects:
    Need to display on buttons First Name, Last Name, Position, Bye Week.

5. Lists sorted by
    a.  ADP Draft Board - simple sorted by ADP
    b.  VBD Draft Board - Sorted by VBD or ECR?  TODO Compare ECR and VBD ranks
    c.  ECR Cheat Sheets:
            ECR with Tier[Player Name, Rank, ECR vs ADP Diff] 5 lists of dicts
            Positional and SuperFlex lists
    d. Blank Draft Board
        i. Create Undrafted list/dataframe from main player pool and pop item each time someone is picked to put on the
            board
        ii.
6. Draft Boards
    a. ADP, VBD, Blank - all implementations from the same player pool.  The blank can/maybe should be a copy?
    b. How to fill in the blank?

Player_Pool = Main Pool should come from ECR/VBD   List of Player Dicts? or DataFrame
    a. List of Player dicts in already in place when implementing to Numpy
        i. sorting is a bit weird
    b. Player Pool should have:
        i. Player Name/Display Name, Position, Bye, Team as a single value to put on buttons.
        ii.
        iii. C

"""

# !/usr/bin/env python
import pdb
import time
import PySimpleGUI as sg
import csv
import pandas as pd
import requests
import numpy as np
from pathlib import Path
import json
from sleeper_wrapper import Drafts, League, Players
from ecr import *  # get_db_arr, get_fpros_data, merge_dfs, get_player_pool, open_keepers, clear_all_keepers, reorder_keepers, DraftIdPopUp
from ffcalc import get_adp_df
from pandastable import Table
from tkinter import *

MAX_ROWS = 17
MAX_COLS = 12
BOARD_LENGTH = MAX_ROWS * MAX_COLS
PP = get_player_pool()


def get_mock_keepers(mock_id=856772332067360768):
    mock_draft = Drafts(mock_id)

    return mock_draft.get_all_picks()


def make_pick_list():
    pl = [f"{r + 1}.{c + 1}" for r in range(MAX_ROWS) for c in range(MAX_COLS)]
    pl = np.array(pl)
    pl = np.reshape(pl, (MAX_ROWS, MAX_COLS))
    pl[1::2, :] = pl[1::2, ::-1]
    pl = pl.flatten()

    return pl.tolist()


def KeeperPopUp():
    global PP
    keeper_list = PP.loc[PP["is_keeper"] == True, 'name'].to_list()
    not_kept_list = PP.loc[PP["is_keeper"] != True, 'name'].to_list()
    # Create pick_list list for window["-KEEPER-PICK-"]
    pick_list = make_pick_list()

    # Create a list of the already established keeper picks and pop them from the pick_list
    kept_picks = PP["pick_no"].loc[PP["is_keeper"] == True].to_list()
    kept_picks.sort(reverse=True)
    print(kept_picks)
    try:
        for pick in kept_picks:
            pick_list.pop(pick - 1)
    except:
        pdb.set_trace()

    col4 = [[sg.Listbox(not_kept_list, key='-DRAFT-POOL-', size=(20, 15), auto_size_text=True,
                        select_mode=sg.LISTBOX_SELECT_MODE_SINGLE)]]
    col5 = [[sg.Text("Pick Player")],
            [sg.Button("Add", key='-ADD-KEEPER-', enable_events=True)],
            [sg.Button("Remove", key='-REMOVE-KEEPER-', enable_events=True)],
            [sg.Button("Set", key='-SET-KEEPER-', enable_events=True)],
            [sg.Button("Clear", key='-CLEAR-KEEPERS-', enable_events=True)],
            [sg.Button("Load Mock Keepers", key='-LOAD-MOCK-KEEPERS-', enable_events=True)],
            [sg.DropDown(pick_list, key='-KEEPER-PICK-', default_value=pick_list[0])],
            [sg.OK()]]
    col6 = [[sg.Listbox(keeper_list, key='-KEEPER-LIST-', size=(20, 15), auto_size_text=True)]]
    window = sg.Window("Set Keepers", [[sg.Column(col4)] + [sg.Column(col5)] + [sg.Column(col6)]])
    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "OK"):
            save_keepers(PP.loc[PP["is_keeper"] == True].to_dict('records'))
            break
        elif event == "-ADD-KEEPER-":
            rd, slot = values["-KEEPER-PICK-"].split('.')
            rd, slot = int(rd), int(slot)
            if rd % 2 == 0:
                pick_no = (rd - 1) * MAX_COLS + MAX_COLS - slot + 1
            else:
                pick_no = (rd - 1) * MAX_COLS + slot
            pick_list.remove(values["-KEEPER-PICK-"])

            # pdb.set_trace()
            k_cols = ["is_keeper", "round", "draft_slot", "pick_no"]
            k_name = ''.join(values["-DRAFT-POOL-"])
            PP.loc[PP["name"] == k_name, k_cols] = [True, rd, slot, pick_no]

            # PP["board_loc"] = PP[[= k_name, "board_loc"] = PP.loc[PP["name"] == k_name
            # pdb.set_trace()
            keeper_list = PP.loc[PP["is_keeper"] == True, 'name'].to_list()
            not_kept_list = PP.loc[PP["is_keeper"] != True, 'name'].to_list()
            #

            # UPDATE ALL 3 Values
            window["-KEEPER-PICK-"].update(values=pick_list, set_to_index=0)
            window["-KEEPER-LIST-"].update(values=keeper_list)
            window["-DRAFT-POOL-"].update(values=not_kept_list)
            pass
        elif event == "-REMOVE-KEEPER-":
            k_cols = ["is_keeper", "round", "draft_slot", "pick_no"]
            k_name = ''.join(values["-KEEPER-LIST-"])

            rd = PP.loc[PP["name"] == k_name, "round"].item()
            draft_slot = PP.loc[PP["name"] == k_name, "draft_slot"].item()
            pick_no = PP.loc[PP["name"] == k_name, "pick_no"].item()
            pick_no -= 1
            pick_list_text = f"{rd}.{draft_slot}"
            pick_list.insert(pick_no, pick_list_text)
            PP.loc[PP["name"] == k_name, k_cols] = [False, None, None, None]
            keeper_list = PP.loc[PP["is_keeper"] == True, 'name'].to_list()
            not_kept_list = PP.loc[PP["is_keeper"] != True, 'name'].to_list()

            window["-KEEPER-PICK-"].update(values=pick_list, set_to_index=0)
            window["-KEEPER-LIST-"].update(values=keeper_list)
            window["-DRAFT-POOL-"].update(values=not_kept_list)
            pass
        elif event == "-SET-KEEPER-":
            # split the keeper-pick value for round, slot and calc for pick_no
            rd, slot = ''.join(values["-KEEPER-PICK-"]).split('.')
            rd, slot = int(rd), int(slot)
            if rd % 2 == 0:
                pick_no = (rd - 1) * MAX_COLS + MAX_COLS - slot + 1
            else:
                pick_no = (rd - 1) * MAX_COLS + slot

            # Assign the keeper values to the dataframe
            k_cols = ["is_keeper", "round", "draft_slot", "pick_no"]
            k_name = ''.join(values["-KEEPER-"])
            PP.loc[PP["name"] == k_name, k_cols] = [True, rd, slot, pick_no]
            # pdb.set_trace()

            # make the keeper list from the dataframe and then save to the JSON
            keeper_list = PP.loc[PP["is_keeper"] == True].to_dict('records')
            # pdb.set_trace()
            with open('data/keepers/keepers.json', 'w') as file:
                json.dump(keeper_list, file, indent=4)

            # get new keeper list text for text box
            keeper_list_text = open_keepers(get="text")
            window["-KEEPER-LIST-"].update(values=keeper_list_text)
            # pdb.set_trace()
            """
            'round': 15, 'roster_id': None, 'player_id': '7606', 'picked_by': '339134645083856896', 'pick_no': 171, 'is_keeper': None, 'draft_slot': 3
            """
        elif event == "-CLEAR-KEEPERS-":
            reset_keepers()  # resets the keeper values in the json and the dataframe
            keeper_list_text = open_keepers(get="text")  # This opens empty list
            window["-KEEPER-LIST-"].update(values=keeper_list_text)
        elif event == "-LOAD-MOCK-KEEPERS-":
            # PP Switch the keeper values on/off
            reset_keepers()  # resets the keeper values in the json and the dataframe
            # get the mock keeper list
            mock_keepers = get_mock_keepers(855693188285992960)
            # fix the column names
            for k in mock_keepers:
                k['sleeper_id'] = k['player_id']
                k['is_keeper'] = True
            # save the mock keepers to the json file
            save_keepers(mock_keepers)
            keeper_list, keeper_list_text = open_keepers()
            # iterate over the keeper list to grab the dict values and assign to the main player_pool dataframe
            k_cols = ['is_keeper', 'pick_no', 'draft_slot', 'round']
            for p in keeper_list:
                id = p['sleeper_id']
                is_keeper = p['is_keeper']
                pick_no = p['pick_no']
                slot = p['draft_slot']
                rd = p['round']
                PP.loc[PP['sleeper_id'] == id, k_cols] = [is_keeper, pick_no, slot, rd]

            window["-KEEPER-LIST-"].update(values=keeper_list_text)
            # print(mock_keepers)
        print(event)
        print(values)
        print(keeper_list)

    window.close()


def reset_keepers():
    clear_all_keepers()  # this clears the keeper_list as [] and overwrites the keepers.json with empty list
    # this resets the columns in the PP DataFrame
    k_cols = ['is_keeper', 'pick_no', 'draft_slot', 'round']
    for k in k_cols:
        PP[k] = None


def save_keepers(keeper_list):
    cols = ["name", "sleeper_id", 'is_keeper', 'pick_no', 'draft_slot', 'round', 'button_text']
    keeper_list = [{k: v for k, v in keeper.items() if k in cols} for keeper in keeper_list]
    keeper_path = Path('data/keepers/keepers.json')
    print(f"Saving {len(keeper_list)} keepers to {keeper_path}")
    with open(keeper_path, 'w') as file:
        json.dump(keeper_list, file, indent=4)
    pass


def TableSimulation():
    """
    Display data in a table format
    """
    global PP
    sg.popup_quick_message('Hang on for a moment, this will take a bit to create....', auto_close=True,
                           non_blocking=True, font='Default 18')

    sg.set_options(element_padding=(0, 0))
    # --- GUI Definitions ------- #
    menu_def = [['File', ['Open', 'Save', 'Exit']],
                ['Draft ID', ['Select Draft ID']],
                ['Player Pool', ['View Player Pool']],
                ['Keepers', ['Set Keepers', 'Clear All Keepers']],
                ['Edit', ['Paste', ['Special', 'Normal', ], 'Undo'], ],
                ['Help', 'About...'], ]
    BOARD_LENGTH = MAX_ROWS * MAX_COLS
    RELIEF_ = "flat"  # "groove" "raised" "sunken" "solid" "ridge"
    BG_COLORS = {"WR": "white on DodgerBlue",
                 "QB": "white on DeepPink",
                 "RB": "white on LimeGreen",
                 "TE": "white on coral",
                 "PK": "white on purple",
                 "DEF": "white on sienna",
                 ".": "white",
                 "-": "black on grey"}

    """
    Get League and user/map
    """
    league = League()
    user_map = league.map_users_to_team_name()
    """
    Get all picks in sleeper draft
    """
    DRAFT_ID = 850087629952249857  # 858793089177886720  # 855693188285992960  # mock 858792885288538112
    DRAFT_ID_2022_WEEZ_LEAGUE = 850087629952249857  # 854953046042583040

    """
    get draft order from weez league, map to the user names, and sort by the draft position
    """
    draft = Drafts(DRAFT_ID_2022_WEEZ_LEAGUE)
    draft_info = draft.get_specific_draft()
    try:
        draft_order = draft_info['draft_order']
        draft_order = {v: user_map[k] for k, v in draft_order.items()}
    except:
        draft_order = [x for x in range(MAX_COLS)]
    # ---- draft_order to be used to create labels above the draft board  -----#

    """
    Now create draft for the mock draft we are using
    """
    draft = Drafts(DRAFT_ID)
    drafted_list = draft.get_all_picks()

    # -------Draftboard Arrays--------#
    adp_db = get_db_arr(PP, "adp")
    vbd_db = get_db_arr(PP, "ecr")
    db = get_db_arr(PP, "empty")

    keeper_pool = PP.loc[PP["is_keeper"] == True].to_dict("records")

    for p in keeper_pool:
        loc = (p["round"] - 1, p["draft_slot"] - 1)
        db[loc] = {"button_text": p["button_text"], "position": p["position"]}

    """
    Cheat Sheet List building
    """
    ecr_cheat = PP.sort_values(by=['superflex_rank_ecr'], ascending=True, na_position='last')
    ecr_cheat = ecr_cheat[['superflex_tier_ecr', 'superflex_rank_ecr', 'position', 'name', 'team', 'sleeper_id']]
    ecr_cheat.fillna(value="-", inplace=True)
    ecr_data = ecr_cheat.values.tolist()

    """
    Column and Tab Layouts
    """
    # noinspection PyTypeChecker
    col1_layout = [[sg.T("  ", size=(5, 1), justification='left')] +
            [sg.B(button_text=draft_order[c + 1], border_width=1, p=(1,1), key=f"TEAM{c}", size=(14, 0)) for c in
             range(MAX_COLS)]] + \
           [[sg.T(f"Rd {str(r + 1)}:", size=(5, 1), justification='left')] +
            [sg.B(button_text=f"{adp_db[r, c]['button_text']}",
                  enable_events=True,
                  size=(14, 0),
                  p=(1, 1),
                  border_width=1,
                  button_color=BG_COLORS[adp_db[r, c]["position"]],
                  mouseover_colors="blue",
                  highlight_colors=("green", "orange"),
                  disabled=False,
                  # changed the disabled_button_color
                  disabled_button_color="white on gray",
                  auto_size_button=True,
                  metadata={"is_clicked": False},
                  # font=("bold"),
                  key=(r, c)) for c in range(MAX_COLS)] for r in
            range(MAX_ROWS)]  # , size=(1200, 796), scrollable=True, expand_x=True, expand_y=True, )

    col1 = sg.Column(col1_layout, size=(1150, 800), scrollable=True, vertical_alignment="bottom", justification="bottom",
                     element_justification="center", pad=5, grab=True)

    tab1_layout = [[sg.T("Cheat Sheets")],
                   [sg.T("QB")], [sg.Listbox(get_cheatsheet_list(PP, "QB"), key='-QB-LIST-TAB-', size=(50, 15),
                                             auto_size_text=True, expand_y=True, expand_x=False, no_scrollbar=False,
                                             horizontal_scroll=False)],
                   [sg.T("RB")],
                   [sg.Listbox(get_cheatsheet_list(PP, "RB"), key="-RB-LIST-TAB-", size=(50, 15), auto_size_text=True,
                               expand_y=True, expand_x=False, no_scrollbar=False, horizontal_scroll=False)],
                   [sg.T("WR")],
                   [sg.Listbox(get_cheatsheet_list(PP, "WR"), key='-WR-LIST-TAB-', size=(50, 15), auto_size_text=True,
                               expand_y=True, expand_x=False, no_scrollbar=False, horizontal_scroll=False)],
                   [sg.T("TE")],
                   [sg.Listbox(get_cheatsheet_list(PP, "TE"), key="-TE-LIST-TAB-", size=(50, 12), auto_size_text=True,
                               expand_y=True, expand_x=False, no_scrollbar=False, horizontal_scroll=False, enable_events=True)]]

    tab2_layout = [[sg.Table(ecr_data, headings=['Tier', 'ECR', 'Pos', 'Name', 'Team', 'sleeper_id'],
                             col_widths=[1, 3, 3, 10, 3], visible_column_map=[True, True, True, True, True, False],
                             auto_size_columns=False, max_col_width=15, display_row_numbers=False,
                             num_rows=min(100, len(ecr_data)), row_height=15, justification="right", expand_x=True,
                             expand_y=True, visible=True, enable_events=True, enable_click_events=True,
                             key="-TAB2-TABLE-", )
                    ]]
    tab1 = sg.Tab("Pos. Cheatsheets", tab1_layout, key="tab1")
    tab2 = sg.Tab("ECR Overall", tab2_layout, key="tab2")
    tab_group = [[sg.TabGroup([[tab1, tab2]], key="tab_group")]]
    col2 = sg.Column(tab_group, size=(300, 796), scrollable=True, grab=True, pad=5)
    pane1 = sg.Pane([col1, col2], orientation = "horizontal",)
    layout = [[sg.Menu(menu_def)],
              [sg.Text('Weez Draftboard', font='Any 18'),
               sg.Button('Load VBD', key="-Load-VBD-"),
               sg.Button('Load ADP', key="-Load-ADP-"),
               sg.Button('Load Draftboard', key="-Load-DB-"),
               sg.Button('Refresh', key="-Refresh-"),
               sg.Text('Search: '),
               sg.Input(key='-Search-', enable_events=True, focus=True, tooltip="Find Player"),
               sg.Combo(values=[f"{x['metadata']['first_name']} {x['metadata']['last_name']}" for x in drafted_list],
                        size=10,
                        enable_events=True,
                        key="-Drafted-")],
              [pane1]]  # [[col1] + [col2]]]
    """
    specifies the font family, size, etc. Tuple or Single string format 'name size styles'. Styles: italic * roman bold normal underline overstrike
    
    """
    window = sg.Window('Table', layout, return_keyboard_events=True, resizable=True, scaling=1)
    """
    WHILE LOOP
    """
    while True:
        event, values = window.read(timeout=1000)

        # --- Process buttons --- #
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        elif event in ("-TAB2-TABLE-", "-TE-LIST-TAB-"):
            pdb.set_trace()
        elif event in ("-Refresh-", sg.TIMEOUT_KEY):
            # drafted = keeper_list
            drafted = [f"{x['metadata']['first_name']} {x['metadata']['last_name']}" for x in draft.get_all_picks()]
            window["-Drafted-"].update(values=drafted)
            # for loop to set the drafted players as "clicked"
            for c in range(MAX_COLS):
                for r in range(MAX_ROWS):
                    cur_player_name = window[(r, c)].get_text()
                    cur_player_name = cur_player_name.replace("\n", " ")
                    for players in drafted:
                        if players in cur_player_name:
                            window[(r, c)].metadata["is_clicked"] = True
                            window[(r, c)].update(button_color='white on gray')
                        else:
                            pass
        elif event == '-Search-':
            search_text = values["-Search-"].lower()
            for c in range(MAX_COLS):
                for r in range(MAX_ROWS):
                    if search_text == "":
                        if window[(r, c)].metadata["is_clicked"]:
                            window[(r, c)].update(button_color='white on gray')
                        else:
                            window[(r, c)].update(button_color=BG_COLORS[db[r, c]["position"]])
                    elif search_text in window[(r, c)].get_text().lower():
                        window[(r, c)].update(button_color="black on yellow")
                    else:
                        if window[(r, c)].metadata["is_clicked"]:
                            window[(r, c)].update(button_color='white on gray')
                        else:
                            window[(r, c)].update(button_color=BG_COLORS[db[r, c]["position"]])
        elif event == '-Drafted-':
            search_text = values["-Drafted-"].lower()
            for player in drafted_list:
                for c in range(MAX_COLS):
                    for r in range(MAX_ROWS):
                        if player in window[(r, c)].get_text().lower():
                            window[(r, c)].update(button_color="gray")
                        else:
                            print("Line 349 - update button color")
                            pdb.set_trace()

                        button_reset_color = f"white on {BG_COLORS[db[r, c]['position']]}"
                        if search_text == "":
                            window[(r, c)].update(button_color=button_reset_color)
                        elif search_text in window[(r, c)].get_text().lower():
                            window[(r, c)].update(button_color="gray")
                        else:
                            window[(r, c)].update(button_color=button_reset_color)
        # click on button event
        elif event in [(r, c) for c in range(MAX_COLS) for r in range(MAX_ROWS)]:
            r, c = event
            window[(r, c)].metadata["is_clicked"] = not window[(r, c)].metadata["is_clicked"]
            if window[(r, c)].metadata["is_clicked"]:
                window[(r, c)].update(button_color='white on gray')
            else:
                window[(r, c)].update(button_color=BG_COLORS[db[r, c]["position"]])
        elif event == "-Load-ADP-":
            # PP.sort_values(by=['adp_pick'], ascending=True, na_position='last',
            #               inplace=True)
            # db = np.array(PP[:MAX_ROWS * MAX_COLS].to_dict("records"))
            # db = np.reshape(db, (MAX_ROWS, MAX_COLS))
            for c in range(MAX_COLS):
                for r in range(MAX_ROWS):
                    window[(r, c)].update(
                        button_color=BG_COLORS[adp_db[r, c]["position"]],
                        text=adp_db[r, c]['button_text']
                    )
        elif event == "-Load-VBD-":
            for c in range(MAX_COLS):
                for r in range(MAX_ROWS):
                    window[(r, c)].update(button_color=BG_COLORS[vbd_db[r, c]["position"]],
                                          text=f"{vbd_db[r, c]['button_text']}")
        elif event == "-Load-DB-":
            # PP.sort_values(by="superflex_rank_ecr", ascending=True, inplace=True)
            # db = np.array(PP[:MAX_ROWS * MAX_COLS].to_dict("records"))
            # db = np.reshape(db, (MAX_ROWS, MAX_COLS))
            # empty_db = np.empty([MAX_ROWS, MAX_COLS])
            # db[1::2, :] = db[1::2, ::-1]
            for c in range(MAX_COLS):
                for r in range(MAX_ROWS):
                    window[(r, c)].update(button_color=BG_COLORS[db[r, c]["position"]], text=db[r, c]['button_text'])
        elif event == "View Player Pool":
            pass
            # ViewPlayerPool()
        elif event == 'About...':
            sg.popup('Demo of table capabilities')
        elif event == 'Set Keepers':
            KeeperPopUp()
        elif event == 'Clear All Keepers':
            sg.popup('Clear All Keepers')
        elif event == 'Select Draft ID':
            sg.PopupScrolled('Select Draft ID')
            # pdb.set_trace()
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
                [window[(i, j)].update('') for j in range(MAX_COLS)
                 for i in range(MAX_ROWS)]

                for i, row in enumerate(data):
                    for j, item in enumerate(row):
                        location = (i, j)
                        try:  # try the best we can at reading and filling the table
                            target_element = window[location]
                            new_value = item
                            if target_element is not None and new_value != '':
                                target_element.update(new_value)
                        except:
                            pass
        elif event == "Set Keeper":
            KeeperPopUp()
        elif event == "Get Live Picks":
            try:
                print(draft.get_all_picks())
                drafted_list = [f"{x['metadata']['first_name']} {x['metadata']['last_name']}" for x in
                                draft.get_all_picks()]
                print(drafted_list[-1])
            except:
                pdb.set_trace()

    # window["-Drafted-"].update(values=drafted_list)

    window.close()


TableSimulation()
