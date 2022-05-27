import pdb
from tkinter import *
import pandas as pd
from pandastable import Table, TableModel, config
from sleeper_wrapper import League, Stats, Players
league_id = 650057741137690624
league = League(league_id)
league.get_league()
# players = Players()
# all_players = players.get_all_players()
s = Stats(2021, scoring_settings=league.scoring_settings)

for p in s.stats.items():
    print(type(p[1]))
pdb.set_trace()
# stats_2021 = stats.get_year_stats(season=2021, scoring_settings=league.scoring_settings, position_list=["RB"])
df = pd.DataFrame.from_dict(stats.stats, orient="index")
col_list = ["name", "age", "position", "pts_custom", "ppg", "gp"]

"""
def get_position_listbox():
    position_list = [position_listbox.get(i) for i in position_listbox.curselection()]
    
    df = pd.DataFrame.from_dict(stats, orient="index")
    col_list = ["name", "age", "position", "pts_custom", "ppg", "gp"]
    df = df[col_list]
    df = df.sort_values("pts_custom", ascending=False)
    table = Table(table_frame, dataframe=stats.df, showtoolbar=True, showstatusbar=True)
    table.autoResizeColumns()
    table.show()
"""

# ------------- GUI SETUP ----------- #
window = Tk()
window.title("Sleeper Project")
table_frame = Frame(window)
table_frame.pack(fill=BOTH, expand=1, side="right")
select_frame = Frame(window)
select_frame.pack(side="left")
"""
temp_button = Button(select_frame, text="Temp", command=get_position_listbox)
temp_button.pack()

position_listbox = Listbox(select_frame, selectmode="multiple")
position_listbox.pack()
position_list = ["QB", "RB", "WR", "TE", "K", "DEF", "TEAM"]
for p in range(len(position_list)):
    position_listbox.insert(END, position_list[p])
    position_listbox.itemconfig(p, bg="lime")
"""
table = Table(table_frame, dataframe=df, showtoolbar=True, showstatusbar=True)
table.autoResizeColumns()
table.show()
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