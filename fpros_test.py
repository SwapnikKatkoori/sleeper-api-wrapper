from fpros import Projections
from sleeper_wrapper import Players
import pandas as pd
from pandastable import Table
from tkinter import *
import json
import time


def make_table(gui_df):
    """
    Table Func for GUI
    """
    table = Table(table_frame, dataframe=gui_df, showtoolbar=True, showstatusbar=True)
    table.autoResizeColumns()
    table.show()

start_time = time.time()

with open('data/adp/adp.json', 'r') as file:
    adp_dict = json.load(file)

adp_df = pd.DataFrame(adp_dict)
search_name_tuples = list(zip(adp_df.search_full_name, adp_df.team))
# print(search_name_tuples)
search_names = adp_df['search_full_name'].to_list()

players = Players()
players_df = players.get_players_df()
# df = players_df[players_df.search_full_name.isin(search_names)]
df = players_df[players_df[['search_full_name', 'team']].apply(tuple, axis=1).isin(search_name_tuples)]
match_search_names = df['search_full_name'].to_list()

missing_search_names = [n for n in search_names if n not in match_search_names]
end_time = time.time()
print(end_time-start_time)
print(f"Length of Match Search Names: {len(match_search_names)}")
print(f"length of search names: {len(search_names)}")
print(f"missing search names {missing_search_names}")
print(f"Length of Missing Search Names {len(missing_search_names)}")
print(f"length of Search names - Missing search names: {len(search_names) - len(missing_search_names)}")
# print(df[df.duplicated(['search_full_name'], keep=False)])




# ------------- GUI SETUP ----------- #


window = Tk()
window.title("Sleeper Project")
table_frame = Frame(window)
table_frame.pack(fill=BOTH, expand=1, side="right")
select_frame = Frame(window)
select_frame.pack(side="left")
make_table(df)

window.mainloop()
