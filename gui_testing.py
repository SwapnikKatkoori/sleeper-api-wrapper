import pdb
from tkinter import *
from tkinter import ttk
import pandas as pd
from pandastable import Table, TableModel, config
from sleeper_wrapper import League, Stats, Players
league_id = 650057741137690624
league = League(league_id)
league.get_league()
# players = Players()
# all_players = players.get_all_players()
stats = Stats(2021, week_start=10, week_stop=18, scoring_settings=league.scoring_settings)

df = pd.DataFrame.from_dict(stats.average_dict, orient="index")
df_cols = list(df)
col_list = ["vbd_custom",
            "pts_custom", "rank_custom", "pos_rank_custom",
            "pts_std", "rank_std",  "pos_rank_std",
            "pts_ppr", "rank_ppr", "pos_rank_ppr",
            "ppg", "gp", "total_gp", "total_gms_active",
            "total_pts_ppr", "total_pts_custom", "total_pts_std", "position", "age", "name"]
# pdb.set_trace()
for cols in col_list:
    col = df.pop(cols)
    df.insert(0, col.name, col)


def get_position_listbox():
    position_listbox_selection = [position_listbox.get(i) for i in position_listbox.curselection()]
    print(position_listbox_selection)
    return position_listbox_selection

def make_table(df):
    table = Table(table_frame, dataframe=df, showtoolbar=True, showstatusbar=True)
    table.autoResizeColumns()
    table.show()

def get_new_stats():
    new_position_list = get_position_listbox()
    year = int(year_combo.get())
    week_start = int(week_start_combo.get())
    week_stop = int(week_stop_combo.get())
    new_stats = Stats(year=year, week_start=week_start, week_stop=week_stop, position_list=new_position_list,
                      scoring_settings=league.scoring_settings)
    new_df = pd.DataFrame.from_dict(new_stats.average_dict, orient="index")
    make_table(new_df)

# ------------- GUI SETUP ----------- #
window = Tk()
window.title("Sleeper Project")
table_frame = Frame(window)
table_frame.pack(fill=BOTH, expand=1, side="right")
select_frame = Frame(window)
select_frame.pack(side="left")
get_button = Button(select_frame, text="Get Stats", command=get_new_stats)
get_button.pack()

year_combo = ttk.Combobox(select_frame, values=[n for n in range(2014, 2022)])
year_combo.set("Year")
year_combo.pack()
week_start_combo = ttk.Combobox(select_frame, values=[n for n in range(1, 19)])
week_start_combo.set("Start Week")
week_start_combo.pack()
week_stop_combo = ttk.Combobox(select_frame, values=[n for n in range(1, 19)])
week_stop_combo.set("Stop Week")
week_stop_combo.pack()
position_listbox = Listbox(select_frame, selectmode="multiple")
position_listbox.pack()
position_list = ["QB", "RB", "WR", "TE", "K", "DEF", "TEAM"]
for p in range(len(position_list)):
    position_listbox.insert(END, position_list[p])
    position_listbox.itemconfig(p)

make_table(df)
# table.pack()

window.mainloop()

"""
class TestApp(Frame):
        
        def __init__(self, parent=None):
            self.parent = parent
            Frame.__init__(self)
            self.main = self.master
            self.main.geometry('600x400+200+100')
            self.main.title('Table app')
            f = Frame(self.main)
            f.pack(fill=BOTH,expand=1)
            df = TableModel.getSampleData()
            self.table = pt = Table(f, dataframe=df,
                                    showtoolbar=True, showstatusbar=True)
                        pt.show()
                        #set some options
                        options = {'colheadercolor':'green','floatprecision': 5}
                        config.apply_options(options, pt)
            pt.show()
            return

app = TestApp()
#launch the app
app.mainloop()
"""