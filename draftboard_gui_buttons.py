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

from sleeper_wrapper import Drafts, League
from draftboard_brain import *
from KeeperPopUp import KeeperPopUp
from LeaguePopUp import LeaguePopUp


def TableSimulation():
    """
    Display data in a table format
    """
    sg.popup_quick_message('Hang on for a moment, this will take a bit to create....', auto_close=True,
                           non_blocking=True, font='Default 18')

    sg.set_options(element_padding=(1, 1))
    sg.set_options(font=("Calibri", 11, "normal"))
    # --- GUI Definitions ------- #
    menu_def = [['File', ['Open', 'Save', 'Exit']],
                ['Draft ID', ['Select Draft ID']],
                ['League', ['Select League']],
                ['Player Pool', ['View Player Pool']],
                ['Keepers', ['Set Keepers', 'Clear All Keepers']],
                ['Edit', ['Paste', ['Special', 'Normal', ], 'Undo'], ],
                ['Help', 'About...'], ]

    RELIEF_ = "flat"  # "groove" "raised" "sunken" "solid" "ridge"
    BG_COLORS = {"WR": "white on DodgerBlue",
                 "QB": "white on DeepPink",
                 "RB": "white on LimeGreen",
                 "TE": "white on coral",
                 "PK": "white on purple",
                 "DEF": "white on sienna",
                 ".": "white",
                 "-": "wheat"}

    MAX_ROWS = 17
    MAX_COLS = 12
    BOARD_LENGTH = MAX_ROWS * MAX_COLS
    PP = get_player_pool()
    BOARD_LENGTH = MAX_ROWS * MAX_COLS

    """
    Get League and user/map
    """
    league = League()
    user_map = league.map_users_to_team_name()
    """
    Get all picks in sleeper draft
    """
    DRAFT_ID = 859302163317399552  #    850087629952249857  # 858793089177886720  # 855693188285992960  # mock 858792885288538112
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
    draft_order = [x for x in range(MAX_COLS+1)]
    # ---- draft_order to be used to create labels above the draft board  -----#

    """
    Now create draft for the mock draft we are using
    """
    draft = Drafts(DRAFT_ID)
    live_draft = False

    if live_draft:
        drafted_list = draft.get_all_picks()
    else:
        drafted_list = PP.loc[PP["is_keeper"] == True, 'sleeper_id'].to_list()

    # -------Draftboard Arrays--------#
    adp_db = get_db_arr(PP, "adp")
    ecr_db = get_db_arr(PP, "ecr")
    db = get_db_arr(PP, "empty")

    # Placing keepers on the empty draft board
    keeper_pool = PP.loc[PP["is_keeper"] == True].to_dict("records")
    for p in keeper_pool:
        loc = (p["round"] - 1, p["draft_slot"] - 1)
        db[loc] = {"button_text": p["button_text"], "position": p["position"]}

    """
    Column and Tab Layouts
    """
    # noinspection PyTypeChecker
    col1_layout = [[sg.T("", size=(3, 1), justification='left')] +
                   [sg.B(button_text=draft_order[c + 1], border_width=0, p=(1, 1), key=f"TEAM{c}", size=(13, 0)) for c
                    in range(MAX_COLS)]] + \
                  [[sg.T(f"R{str(r + 1)}", size=(3, 1), justification='left')] +
                   [sg.B(button_text=f"{db[r, c]['button_text']}",
                         enable_events=True,
                         size=(13, 0),
                         p=(1, 1),
                         border_width=0,
                         button_color=BG_COLORS[db[r, c]["position"]],
                         mouseover_colors="gray",
                         disabled=False,
                         disabled_button_color="white on gray",
                         highlight_colors=("black", "white"),
                         auto_size_button=True,
                         metadata={"is_clicked":  False,   # False,  # Leave this off by default #
                                   "button_color": BG_COLORS[db[r, c]["position"]],
                                   "sleeper_id": "",
                                   },
                         key=(r, c)) for c in range(MAX_COLS)] for r in
                   range(MAX_ROWS)]  # , size=(1200, 796), scrollable=True, expand_x=True, expand_y=True, )

    col1 = sg.Column(col1_layout, size=(1150, 800), scrollable=True, vertical_alignment="bottom",
                     justification="bottom",
                     element_justification="left", pad=5, grab=True)

    # New layouts for Tabs containing tables:
    tab1_layout = [[sg.T("Cheat Sheets")],
                   [get_cheatsheet_table(PP, pos="QB", hide_drafted=False)],
                   [get_cheatsheet_table(PP, pos="RB", hide_drafted=False)],
                   [get_cheatsheet_table(PP, pos="WR", hide_drafted=False)],
                   [get_cheatsheet_table(PP, pos="TE", hide_drafted=False)],
                   ]
    tab2_layout = [[get_cheatsheet_table(PP, pos="ALL", hide_drafted=False)]]

    # ---Cheatsheet for tables in Tabs---#
    tab1 = sg.Tab("Pos. Cheatsheets", tab1_layout, key="tab1")
    tab2 = sg.Tab("ECR Overall", tab2_layout, key="tab2")
    #------ Put Tabs in Groups and then in a Pane ------ #
    tab_group = [[sg.TabGroup([[tab1, tab2]], key="tab_group")]]
    col2 = sg.Column(tab_group, size=(300, 796), scrollable=True, grab=True, pad=5)
    pane1 = sg.Pane([col1, col2], orientation="horizontal", )
    layout = [[sg.Menu(menu_def)],
              [sg.Text('Weez Draftboard', font='Any 18'),
               sg.Button('Load ECR', key="-Load-ECR-"),
               sg.Button('Load ADP', key="-Load-ADP-"),
               sg.Button('Load Draftboard', key="-LOAD-DB-"),
               sg.Button('Refresh', key="-Refresh-"),
               sg.Text('Search: '),
               sg.Input(key='-Search-', enable_events=True, focus=True, tooltip="Find Player"),
               sg.Push(),
               sg.Checkbox("Hide Drafted Players", enable_events=True, key="-HIDE-DRAFTED-")],
              [pane1]]

    window = sg.Window('Weez Draftboard',
                       layout, return_keyboard_events=True, resizable=True, scaling=2, right_click_menu_tearoff=1)
    """
    WHILE LOOP
    """
    while True:
        event, values = window.read(timeout=1000)

        # --- Process buttons --- #
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        # click on button event
        elif event == "-HIDE-DRAFTED-":
            for t in ["ALL", "QB", "WR", "TE", "RB"]:
                table_data = get_cheatsheet_data(PP, pos=t, hide_drafted=window["-HIDE-DRAFTED-"].get())
                window[f"-{t}-TABLE-"].update(values=table_data)

        elif event in [(r, c) for c in range(MAX_COLS) for r in range(MAX_ROWS)]:
            r, c = event
            s_id = window[(r, c)].metadata["sleeper_id"]
            print(f"Current ID: {s_id}")
            window[(r, c)].metadata["is_clicked"] = not window[(r, c)].metadata["is_clicked"]
            if window[(r, c)].metadata["is_clicked"]:
                window[(r, c)].update(button_color='white on gray')
                PP.loc[PP["sleeper_id"] == s_id, "is_drafted"] = True
                for t in ["ALL", "QB", "WR", "TE", "RB"]:
                    table_data = get_cheatsheet_data(PP, pos=t, hide_drafted=window["-HIDE-DRAFTED-"].get())
                    window[f"-{t}-TABLE-"].update(values=table_data)
            else:
                window[(r, c)].update(button_color=window[(r, c)].metadata["button_color"])
                PP.loc[PP["sleeper_id"] == s_id, "is_drafted"] = False
                for t in ["ALL", "QB", "WR", "TE", "RB"]:
                    table_data = get_cheatsheet_data(PP, pos=t, hide_drafted=window["-HIDE-DRAFTED-"].get())
                    window[f"-{t}-TABLE-"].update(values=table_data)
        elif event in ("-Refresh-", sg.TIMEOUT_KEY):
            # drafted = keeper_list
            if live_draft:
                all_picks = draft.get_all_picks()
                # drafted = [f"{x['metadata']['first_name']} {x['metadata']['last_name']}" for x in all_picks]
                drafted_ids = [x['player_id'] for x in all_picks]
            else:
                drafted_ids = PP.loc[PP["is_drafted"] == True, "sleeper_id"].tolist()
            PP.loc[PP["sleeper_id"].isin(drafted_ids), "is_drafted"] = True
            for t in ["ALL", "QB", "WR", "TE", "RB"]:
                table_data = get_cheatsheet_data(PP, pos=t, hide_drafted=window["-HIDE-DRAFTED-"].get())
                window[f"-{t}-TABLE-"].update(values=table_data)
            # for loop to set the drafted players as "clicked"
            for c in range(MAX_COLS):
                for r in range(MAX_ROWS):
                    cur_id = window[(r, c)].metadata['sleeper_id']
                    # cur_player_name = cur_player_name.replace("\n", " ")
                    if cur_id in drafted_ids:
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
        elif event == "-Load-ADP-":
            for c in range(MAX_COLS):
                for r in range(MAX_ROWS):
                    window[(r, c)].update(button_color=BG_COLORS[adp_db[r, c]["position"]],
                                          text=adp_db[r, c]['button_text'], )
                    window[(r, c)].metadata["button_color"] = BG_COLORS[adp_db[r, c]["position"]]
                    window[(r, c)].metadata["sleeper_id"] = adp_db[r, c]["sleeper_id"]
        elif event == "-Load-ECR-":
            for c in range(MAX_COLS):
                for r in range(MAX_ROWS):
                    window[(r, c)].update(button_color=BG_COLORS[ecr_db[r, c]["position"]],
                                          text=f"{ecr_db[r, c]['button_text']}")
                    window[(r, c)].metadata["button_color"] = BG_COLORS[ecr_db[r, c]["position"]]
                    window[(r, c)].metadata["sleeper_id"] = ecr_db[r, c]["sleeper_id"]
        elif event == "-LOAD-DB-":
            for c in range(MAX_COLS):
                for r in range(MAX_ROWS):
                    window[(r, c)].update(button_color=BG_COLORS[db[r, c]["position"]], text=db[r, c]['button_text'])

        elif event == "View Player Pool":
            pass
            # ViewPlayerPool()
        elif event == 'About...':
            sg.popup('Demo of table capabilities')
        elif event == 'Set Keepers':
            PP = KeeperPopUp(PP)
            # Refresh Arrays after Keeper Pop Up
            adp_db = get_db_arr(PP, "adp")
            ecr_db = get_db_arr(PP, "ecr")
            db = get_db_arr(PP, "empty")

            # Placing keepers on the empty draft board
            keeper_pool = PP.loc[PP["is_keeper"] == True].to_dict("records")
            for p in keeper_pool:
                loc = (p["round"] - 1, p["draft_slot"] - 1)
                db[loc] = {"button_text": p["button_text"], "position": p["position"]}
            window["-LOAD-DB-"].click()
        elif event == 'Clear All Keepers':
            sg.popup('Clear All Keepers')
        elif event == 'Select Draft ID':
            sg.PopupScrolled('Select Draft ID')
            # pdb.set_trace()
        elif event == "Get Live Picks":
            try:
                print(draft.get_all_picks())
                drafted_list = [f"{x['metadata']['first_name']} {x['metadata']['last_name']}" for x in
                                draft.get_all_picks()]
                print(drafted_list[-1])
            except:
                pass
    window.close()


TableSimulation()

"""
      
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
        
        
"""
