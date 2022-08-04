import PySimpleGUI as sg
from draftboard_brain import *
import pdb

def KeeperPopUp(df):

    keeper_list = df.loc[df["is_keeper"] == True, 'name'].to_list()
    not_kept_list = df.loc[df["is_keeper"] != True, 'name'].to_list()
    # Create pick_list list for window["-KEEPER-PICK-"]
    pick_list = make_pick_list()

    # Create a list of the already established keeper picks and pop them from the pick_list
    kept_picks = df["pick_no"].loc[df["is_keeper"] == True].to_list()
    kept_picks.sort(reverse=True)
    print(kept_picks)
    try:
        for pick in kept_picks:
            pick_list.pop(pick - 1)
    except:
        pdb.set_trace()

    filter_tooltip = "Find Player"

    col4 = [[sg.Input(size=(20, 1), focus=True, enable_events=True, key='-FILTER-', tooltip=filter_tooltip)],
            [sg.Listbox(not_kept_list, key='-DRAFT-POOL-', size=(20, 15), auto_size_text=True,
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
            save_keepers(df.loc[df["is_keeper"] == True].to_dict('records'))
            break
        elif event == "-FILTER-":
            new_list = [i for i in not_kept_list if values['-FILTER-'].lower() in i.lower()]
            window['-DRAFT-POOL-'].update(new_list)
        elif event == "-ADD-KEEPER-":
            rd, slot = values["-KEEPER-PICK-"].split('.')
            rd, slot = int(rd), int(slot)
            if rd % 2 == 0:
                pick_no = (rd - 1) * MAX_COLS + MAX_COLS - slot + 1
            else:
                pick_no = (rd - 1) * MAX_COLS + slot
            pick_list.remove(values["-KEEPER-PICK-"])

            # pdb.set_trace()
            k_cols = ["is_keeper", "is_drafted", "round", "draft_slot", "pick_no"]
            k_name = ''.join(values["-DRAFT-POOL-"])
            df.loc[df["name"] == k_name, k_cols] = [True, True, rd, slot, pick_no]

            # df["board_loc"] = df[[= k_name, "board_loc"] = df.loc[df["name"] == k_name
            # pdb.set_trace()
            keeper_list = df.loc[df["is_keeper"] == True, 'name'].to_list()
            not_kept_list = df.loc[df["is_keeper"] != True, 'name'].to_list()
            #

            # UPDATE ALL 3 Values
            window["-KEEPER-PICK-"].update(values=pick_list, set_to_index=0)
            window["-KEEPER-LIST-"].update(values=keeper_list)
            window["-DRAFT-POOL-"].update(values=not_kept_list)
            pass
        elif event == "-REMOVE-KEEPER-":
            k_cols = ["is_keeper", "is_drafted", "round", "draft_slot", "pick_no"]
            k_name = ''.join(values["-KEEPER-LIST-"])

            rd = df.loc[df["name"] == k_name, "round"].item()
            draft_slot = df.loc[df["name"] == k_name, "draft_slot"].item()
            pick_no = df.loc[df["name"] == k_name, "pick_no"].item()
            pick_no -= 1
            pick_list_text = f"{rd}.{draft_slot}"
            pick_list.insert(pick_no, pick_list_text)
            df.loc[df["name"] == k_name, k_cols] = [False, False, None, None, None]
            keeper_list = df.loc[df["is_keeper"] == True, 'name'].to_list()
            not_kept_list = df.loc[df["is_keeper"] != True, 'name'].to_list()

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
            k_cols = ["is_keeper", "is_drafted", "round", "draft_slot", "pick_no"]
            k_name = ''.join(values["-KEEPER-"])
            df.loc[df["name"] == k_name, k_cols] = [True, True, rd, slot, pick_no]
            # pdb.set_trace()

            # make the keeper list from the dataframe and then save to the JSON
            keeper_list = df.loc[df["is_keeper"] == True].to_dict('records')
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
            df = reset_keepers(df)  # resets the keeper values in the json and the dataframe
            keeper_list_text = open_keepers(get="text")  # This opens empty list
            window["-KEEPER-LIST-"].update(values=keeper_list_text)
        elif event == "-LOAD-MOCK-KEEPERS-":
            # df Switch the keeper values on/off
            df = reset_keepers(df)  # resets the keeper values in the json and the dataframe
            # get the mock keeper list
            mock_keepers = get_mock_keepers(855693188285992960)
            # fix the column names
            for k in mock_keepers:
                k['sleeper_id'] = k['player_id']
                k['is_keeper'] = True
                k['is_drafted'] = False
            # save the mock keepers to the json file
            save_keepers(mock_keepers)
            keeper_list, keeper_list_text = open_keepers()
            # iterate over the keeper list to grab the dict values and assign to the main player_pool dataframe
            k_cols = ['is_keeper', 'pick_no', 'draft_slot', 'round']
            for p in keeper_list:
                id = p['sleeper_id']
                is_keeper = p['is_keeper']
                is_drafted = p["is_drafted"]
                pick_no = p['pick_no']
                slot = p['draft_slot']
                rd = p['round']
                df.loc[df['sleeper_id'] == id, k_cols] = [is_keeper, is_drafted, pick_no, slot, rd]

            window["-KEEPER-LIST-"].update(values=keeper_list_text)
            # print(mock_keepers)
        print(event)
        print(values)
        print(keeper_list)

    window.close()
    return df
