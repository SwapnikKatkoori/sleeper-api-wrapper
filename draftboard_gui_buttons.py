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
from ecr import get_fpros_data, merge_dfs, get_player_pool
from ffcalc import get_adp_df

BOARD_LENGTH = 192

MAX_ROWS = 17
MAX_COLS = 12
PLAYER_POOL = get_player_pool()
"""
def get_player_pool():
    # first get the fantasy pros data/projections as dataframe

    fpros_df = get_fpros_data(player_count=225)
    adp_df = get_adp_df()
    adp_df.drop(['name', 'team', 'position', 'bye'], axis=1, inplace=True)
    pool_df = merge_dfs(fpros_df, adp_df, "sleeper_id", how="outer")
    pool_df.fillna(value="DEF", inplace=True)
    pdb.set_trace()
    # Then get the ADP Dataframe and Merge
    # adp_df = get_adp_df()
    # cols_to_use = adp_df.columns.difference(fpros_df.columns).to_list()
    # cols_to_use.append("sleeper_id")
    # pool_df = pd.merge(fpros_df, adp_df[cols_to_use], on="sleeper_id", how="left")
    # nan_rows = pool_df[pool_df["name"].isnull()]
    # nan_rows = adp_df[adp_df["name"].isnull()]

    pool_df["button_text"] = pool_df['first_name'] + '\n' + pool_df['last_name'] + '\n' + pool_df['position'] + ' (' \
                             + pool_df['team'] + ') ' + pool_df['bye'].astype(str)

    # pool_df['name'] + "\n(" + pool_df['team'] + ")\n" + pool_df['bye'].astype(str)

    pool_df.to_csv('data/player_pool/pool_df.csv')
    # pdb.set_trace()
    return pool_df
"""


def sort_table(table, cols):
    """ sort a table by multiple columns
        table: a list of lists (or tuple of tuples) where each inner list
               represents a row
        cols:  a list (or tuple) specifying the column numbers to sort by
               e.g. (1,0) would sort by column 1, then by column 0
    """
    for col in reversed(cols):
        try:
            table = sorted(table, key=operator.itemgetter(col))
        except Exception as e:
            sg.popup_error('Error in sort_table', 'Exception in sort_table', e)
    return table


def get_mock_keepers(mock_id=856772332067360768):
    mock_draft = Drafts(mock_id)
    return mock_draft.get_all_picks()


def reorder_keepers(list_to_sort, keeper_list):
    print(f"Before Keeper Insert {len(list_to_sort)}")
    pop_count = 0
    for k in keeper_list:
        k['name'] = f"{k['metadata']['first_name']} {k['metadata']['last_name']}"
        k['position'] = k['metadata']['position']
        k['team'] = k['metadata']['team']
        for i, d in enumerate(list_to_sort):
            try:
                if d['sleeper_id'] == k['player_id']:
                    k['bye'] = d['bye']
                    list_to_sort.pop(i)
                    pop_count += 1
                    pass
            except:
                print("This Key Error")
                pdb.set_trace()

    print(f"Total Popped {pop_count}")
    # sorting the keeper list by the pick
    keeper_list = sorted(keeper_list, key=lambda k: k['pick_no'])
    # inserting all keepers in keeper_list back into adp_list
    for k in keeper_list:
        list_to_sort.insert(k['pick_no'] - 1, k)

    print(f"Length after Keeper Insert {len(list_to_sort)}")
    return list_to_sort


def TableSimulation():
    """
    Display data in a table format
    """

    sg.popup_quick_message('Hang on for a moment, this will take a bit to create....', auto_close=True,
                           non_blocking=True, font='Default 18')

    sg.set_options(element_padding=(0, 0))

    menu_def = [['File', ['Open', 'Save', 'Exit']],
                ['Edit', ['Paste', ['Special', 'Normal', ], 'Undo'], ],
                ['Help', 'About...'], ]

    MAX_ROWS = 17
    MAX_COLS = 12

    BOARD_LENGTH = MAX_ROWS * MAX_COLS
    RELIEF_ = "solid"  # "groove" "raised" "sunken" "flat" "ridge"
    BG_COLORS = {"WR": "white on DodgerBlue",
                 "QB": "white on DeepPink",
                 "RB": "white on LimeGreen",
                 "TE": "white on coral",
                 "PK": "white on purple",
                 "DEF": "white on sienna",
                 ".": "white"}

    """
    Get League and user/map
    """
    league = League()
    user_map = league.map_users_to_team_name()
    """
    Get all picks in sleeper draft
    """
    DRAFT_ID = 856772332067360768  # mock
    DRAFT_ID_2022_WEEZ_LEAGUE = 850087629952249857  # 854953046042583040

    """
    get draft order from weez league, map to the user names, and sort by the draft position
    """
    draft = Drafts(DRAFT_ID_2022_WEEZ_LEAGUE)
    draft_info = draft.get_specific_draft()
    draft_order = draft_info['draft_order']
    draft_order = {v: user_map[k] for k, v in draft_order.items()}
    # ---- draft_order to be used to create labels above the draft board  -----#

    """
    Now create draft for the mock draft we are using
    """
    draft = Drafts(DRAFT_ID)
    drafted_list = draft.get_all_picks()
    keeper_list = get_mock_keepers()

    PLAYER_POOL.sort_values(by=['adp_pick'], ascending=True, na_position='last', inplace=True)
    db = np.array(PLAYER_POOL[:MAX_ROWS * MAX_COLS].to_dict("records"))

    rb_list = PLAYER_POOL[PLAYER_POOL["position"] == "RB"].sort_values(by="position_rank_ecr").to_dict("records")

    temp_list = PLAYER_POOL[PLAYER_POOL["position"] == "RB"].groupby('position_tier_ecr')['name'].apply(list)
    rb_pool = PLAYER_POOL[PLAYER_POOL["position"] == "RB"]
    temp_list.transpose()

    db = np.reshape(db, (MAX_ROWS, MAX_COLS))
    db[1::2, :] = db[1::2, ::-1]

    empty_db = np.empty([MAX_ROWS, MAX_COLS])

    """
    TODO: Map and create right-click menus,
    Sort by ADP or VBD or VOLS or VORP
    Create Keeper method
    """

    filter_tooltip = "Find player"

    # noinspection PyTypeChecker
    col1 = [[sg.T("  ", size=(5, 1), justification='left')] +
            [sg.B(button_text=draft_order[c + 1], border_width=1, key=f"TEAM{c}", size=(14, 0)) for c in
             range(MAX_COLS)]] + \
           [[sg.T(f"Rd {str(r + 1)}:", size=(5, 1), justification='left')] +
            [sg.B(button_text=f"{db[r, c]['button_text']}",
                  enable_events=True,
                  size=(14, 0),
                  p=(0, 0),
                  border_width=1,
                  button_color=BG_COLORS[db[r, c]["position"]],
                  mouseover_colors="gray",
                  highlight_colors=("black", "white"),
                  disabled=False,
                  # changed the disabled_button_color
                  disabled_button_color="white on gray",
                  auto_size_button=True,
                  metadata={"is_clicked": False},
                  key=(r, c)) for c in range(MAX_COLS)] for r in
            range(MAX_ROWS)]  # , size=(1200, 796), scrollable=True, expand_x=True, expand_y=True, )

    col2 = [[sg.T("Cheat Sheets")],
            [sg.T("QB")],
            [sg.Listbox(['QB ' + str(i) for i in range(1, 26)], key='-QB-LIST-', size=(20, 15), auto_size_text=True,
                        expand_y=True, expand_x=False, no_scrollbar=False, horizontal_scroll=False)],
            [sg.T("RB")],
            [sg.Listbox([str(p['position_tier_ecr']) + ' ' + p['name'] for p in rb_list], key="-RB-LIST-",
                        size=(20, 15), auto_size_text=True,
                        expand_y=True, expand_x=False, no_scrollbar=False, horizontal_scroll=False)],
            [sg.T("WR")],
            [sg.Listbox(['WR ' + str(i) for i in range(1, 26)], key='-WR-LIST-', size=(20, 15), auto_size_text=True,
                        expand_y=True, expand_x=False, no_scrollbar=False, horizontal_scroll=False)],
            [sg.T("TE")],
            [sg.Listbox(['TE ' + str(i) for i in range(1, 26)], key="-TE-LIST-", size=(20, 12), auto_size_text=True,
                        expand_y=True, expand_x=False, no_scrollbar=False, horizontal_scroll=False)]]

    ecr_cheat = PLAYER_POOL.sort_values(by=['superflex_rank_ecr'], ascending=True, na_position='last')
    ecr_cheat = ecr_cheat[['superflex_tier_ecr', 'superflex_rank_ecr', 'position', 'name', 'team', 'sleeper_id']]

    temp_list = PLAYER_POOL[PLAYER_POOL["position"] == "RB"].groupby('position_tier_ecr')['name'].apply(list)

    ecr_cheat.fillna(value="-", inplace=True)
    ecr_group = ecr_cheat.groupby('superflex_tier_ecr')['name'].apply(list)
    ecr_data = ecr_cheat.values.tolist()
    ecr_columns = ecr_cheat.columns.tolist()
    pdb.set_trace()
    col3 = [[sg.Table(ecr_data,
                      headings=['Tier', 'ECR', 'Pos', 'Team', 'Name', 'sleeper_id'],
                      col_widths=3,
                      visible_column_map=[True, True, True, True, False],
                      cols_justification=None,
                      def_col_width=None,
                      auto_size_columns=True,
                      max_col_width=15,
                      select_mode=None,
                      display_row_numbers=False,
                      num_rows=min(100, len(ecr_data)),
                      row_height=10,
                      font=None,
                      justification="left",
                      text_color=None,
                      background_color=None,
                      alternating_row_color=None,
                      selected_row_colors=(None, None),
                      header_text_color=None,
                      header_background_color=None,
                      header_font=None,
                      header_border_width=None,
                      header_relief=None,
                      row_colors=None,
                      vertical_scroll_only=False,
                      hide_vertical_scroll=False,
                      border_width=None,
                      sbar_trough_color=None,
                      sbar_background_color=None,
                      sbar_arrow_color=None,
                      sbar_width=None,
                      sbar_arrow_width=None,
                      sbar_frame_color=None,
                      sbar_relief=None,
                      size=(None, None),
                      s=(600, 796),
                      change_submits=False,
                      enable_events=False,
                      enable_click_events=True,
                      right_click_selects=True,
                      bind_return_key=False,
                      pad=None,
                      p=None,
                      key="-TABLE-",
                      k=None,
                      tooltip=None,
                      right_click_menu=None,
                      expand_x=True,
                      expand_y=True,
                      visible=True,
                      metadata=None)

             ]]
    col1 = sg.Column(col1, size=(1200, 796), vertical_alignment="bottom", justification="bottom",
                     element_justification="center")
    col2 = sg.Column(col2, size=(150, 796))
    col3 = sg.Column(col3, size=(150, 796))
    cheat_frame = sg.Frame("Cheat Sheets", [[col3, col2]], )
    layout = [[sg.Menu(menu_def)],
              [sg.Text('Weez Draftboard', font='Any 18'),
               sg.Button('Load VBD', key="-Load-VBD-"),
               sg.Button('Load ADP', key="-Load-ADP-"),
               sg.Button('Refresh', key="-Refresh-"),
               sg.Text('Search: '),
               sg.Input(key='-Search-', enable_events=True, focus=True, tooltip=filter_tooltip),
               sg.Combo(values=[f"{x['metadata']['first_name']} {x['metadata']['last_name']}" for x in drafted_list],
                        size=15,
                        enable_events=True,
                        key="-Drafted-")],
              [sg.Column([[col1] + [cheat_frame]], vertical_alignment="bottom", justification="bottom", scrollable=True, size=(
                  1500,
                  800))]]  # , size=(1200, 796), scrollable=False), sg.Column(col2, size=(150, 796), scrollable=False)]]

    window = sg.Window('Table', layout, return_keyboard_events=True, resizable=True, scaling=1)
    # window["-TABLE-"].bind('<Double-Button-1>', "+-double click-")
    while True:
        event, values = window.read(timeout=1000)

        # --- Process buttons --- #
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
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
            PLAYER_POOL.sort_values(by=['adp_pick'], ascending=True, na_position='last',
                                    inplace=True)
            db = np.array(PLAYER_POOL[:MAX_ROWS * MAX_COLS].to_dict("records"))
            db = np.reshape(db, (MAX_ROWS, MAX_COLS))
            for c in range(MAX_COLS):
                for r in range(MAX_ROWS):
                    window[(r, c)].update(
                        button_color=BG_COLORS[db[r, c]["position"]],
                        text=db[r, c]['button_text']
                    )
        elif event == "-Load-VBD-":
            PLAYER_POOL.sort_values(by="superflex_rank_ecr", ascending=True, inplace=True)
            db = np.array(PLAYER_POOL[:MAX_ROWS * MAX_COLS].to_dict("records"))
            db = np.reshape(db, (MAX_ROWS, 12))
            db[1::2, :] = db[1::2, ::-1]
            for c in range(MAX_COLS):
                for r in range(MAX_ROWS):
                    window[(r, c)].update(button_color=BG_COLORS[db[r, c]["position"]],
                                          text=f"{db[r, c]['button_text']}")

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

            # if a valid table location entered, change that location's value
            try:
                player_name = window['Keeper Combo'].get()
                # print(player_name)
                player_index = next((i for (i, d) in enumerate(adp_list) if d["name"] == player_name), None)
                keeper_dict = adp_list.pop(player_index)
                keeper_dict["keeper"] = True
                keeper_dict["keeper_location"] = (int(values['-Keeper Round-'] - 1), int(values['-Keeper Pick-'] - 1))
                adp_list.append(keeper_dict)
                db = np.array(adp_list)
                db = np.reshape(db, (MAX_ROWS, 12))
                db[1::2, :] = db[1::2, ::-1]
                print(db)

                # location = (int(values['inputrow']), int(values['inputcol']))
                target_element = window[keeper_dict['keeper_location']]
                new_value = f"{keeper_dict['name'].split(' ', 1)[0]}\n" \
                            f"{keeper_dict['name'].split(' ', 1)[1]}\n" \
                            f"{keeper_dict['position']} ({keeper_dict['team']}) {keeper_dict['bye']}"
                if target_element is not None and new_value != '':
                    target_element.update(new_value)

            except:
                pass
    # TODO uncomment this block
    """
    try:
        print(draft.get_all_picks())
        drafted_list = [f"{x['metadata']['first_name']} {x['metadata']['last_name']}" for x in draft.get_all_picks()]
        print(drafted_list[-1])
    except:
        pdb.set_trace()
    # window["-Drafted-"].update(values=drafted_list)
    
    """
    window.close()


TableSimulation()

"""


"""
"""
    #OG coolumn layout
    column_layout = [[sg.T(f"Rd {str(r + 1)}:", size=(5, 1), justification='left')] +
                     [sg.B(button_text=f"{db[r, c]['name'].split(' ', 1)[0]}\n"f"{db[r, c]['name'].split(' ', 1)[1]}\n"f"{db[r, c]['position']} ({db[r, c]['team']}) {db[r, c]['bye']}",
                         enable_events=True,
                         size=(14, 0),
                         p=(0, 0),
                         border_width=1,
                         button_color=BG_COLORS[db[r, c]["position"]],
                         mouseover_colors="gray",
                         highlight_colors=("black", "white"),
                         disabled=False,
                         # changed the disabled_button_color
                         disabled_button_color="white on gray",
                         auto_size_button=False,
                         metadata={"is_clicked": False},
                         key=(r, c)
                     )
                         for c in range(MAX_COL)] for r in range(MAX_ROWS)]
    layout = [[sg.Menu(menu_def)],
              [sg.Text('Weez Draftboard', font='Any 18'),

               sg.Button('Load VBD', key="-Load-VBD-"),
               sg.Button('Load ADP', key="-Load-ADP-"),
               sg.Button('Refresh', key="-Refresh-"),
               sg.Combo(values=[f"{x['metadata']['first_name']} {x['metadata']['last_name']}" for x in drafted_list],
                        size=15,
                        enable_events=True,
                        key="-Drafted-"),
               sg.Text('Search: '),
               sg.Input(key='-Search-', enable_events=True, focus=True, tooltip=filter_tooltip)],
            [sg.Col(column_layout, size=(1200, 796), scrollable=True)]]
    """
"""
remove from layout
               sg.Combo(
               values=[x['name'] for x in adp_list],
               default_value=adp_list[0]['name'],
               readonly=False,
               size=(14, 10),
               enable_events=True,
               k='Keeper Combo'),
           sg.Text('Round'),
           sg.Combo(values=[x + 1 for x in range(MAX_ROWS)], default_value=1, key="-Keeper Round-"),
           sg.Text('Pick'),
           sg.Combo(values=[x + 1 for x in range(12)], default_value=1, key="-Keeper Pick-"),
           sg.Button('Set Keeper'),
# -------FROM SCRATCH-------- #
col1 = sg.Column([
    [sg.Frame('Draft Board: ', [[sg.T("  ", size=(5, 1), justification='left')] + [sg.B(button_text=draft_order[c+1], border_width=1, key=f"TEAM{c}", size=(14, 0)) for c in range(MAX_COL)]] + \
    [[sg.T(f"Rd {str(r + 1)}:", size=(5, 1), justification='left')] +
                 [sg.B(
                     button_text=f"{db[r, c]['name'].split(' ', 1)[0]}\n"
                                 f"{db[r, c]['name'].split(' ', 1)[1]}\n"
                                 f"{db[r, c]['position']} ({db[r, c]['team']}) {db[r, c]['bye']}",
                     enable_events=True,
                     size=(14, 0),
                     p=(0, 0),
                     border_width=1,
                     button_color=BG_COLORS[db[r, c]["position"]],
                     mouseover_colors="gray",
                     highlight_colors=("black", "white"),
                     disabled=False,
                     # changed the disabled_button_color
                     disabled_button_color="white on gray",
                     auto_size_button=False,
                     metadata={"is_clicked": False},
                     key=(r, c)
                 )
                     for c in range(MAX_COL)] for r in range(MAX_ROWS)])]])
col2 = sg.Column([
    [sg.Frame("Cheat Sheets: ", [sg.Multiline()])]])
layout = [[sg.Menu(menu_def)],
          [sg.Text('Weez Draftboard', font='Any 18'),

           sg.Button('Load VBD', key="-Load-VBD-"),
           sg.Button('Load ADP', key="-Load-ADP-"),
           sg.Button('Refresh', key="-Refresh-"),
           sg.Combo(values=[f"{x['metadata']['first_name']} {x['metadata']['last_name']}" for x in drafted_list],
                    size=15,
                    enable_events=True,
                    key="-Drafted-"),
           sg.Text('Search: '),
           sg.Input(key='-Search-', enable_events=True, focus=True, tooltip=filter_tooltip)],
          [col1, col2]]
          # [sg.Col(column_layout, size=(1200, 796), scrollable=True)]]


"""
