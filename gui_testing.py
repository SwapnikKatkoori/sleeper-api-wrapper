from tkinter import *
import pandas as pd
from pandastable import Table, TableModel, config
from sleeper_wrapper import League, Stats, Players
league_id = 650057741137690624
league = League(league_id)
league.get_league()
players = Players()
# all_players = players.get_all_players()
stats = Stats()
stats_2021 = stats.get_year_stats(2021)
df = pd.DataFrame.from_dict(stats_2021, orient="index")

# ------------- GUI SETUP ----------- #
window = Tk()
window.title("Sleeper Project")
frame = Frame(window)
frame.pack()
table = Table(Frame, dataframe=df)
table.pack()

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