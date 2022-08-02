from draftboard_brain import *
import pdb
import PySimpleGUI as sg
from pathlib import Path
import json
import pandas as pd

def ViewPlayerPool(df):
    headings = df.columns.tolist()
    table_data = df.values.tolist()
    table = sg.Table(table_data, headings=headings, vertical_scroll_only=False)

    window = sg.Window("Player Pool", layout=[[table]], size=(800, 600))
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            # save_keepers(df.loc[df["is_keeper"] == True].to_dict('records'))
            break
    window.close()
    return
