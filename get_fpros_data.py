from fpros import Projections
from sleeper_wrapper import Players
import pandas as pd
from pandastable import Table
from tkinter import *
import json
import time
import requests
import pandas as pd



start_time = time.time()
url = "https://s3-us-west-1.amazonaws.com/fftiers/out/weekly-ALL-PPR.csv"
r = requests.get(url)
print(r)
open('temp.csv', 'wb').write(r.content)

df = pd.read_csv('temp.csv', sep=',')
print(df.head(30))


end_time = time.time()
print(f"Length of func: {end_time - start_time}")







# ------------- GUI SETUP ----------- #

"""

def make_table(gui_df):
    
    # Table Func for GUI
    
    table = Table(table_frame, dataframe=gui_df, showtoolbar=True, showstatusbar=True)
    table.autoResizeColumns()
    table.show()
window = Tk()
window.title("Sleeper Project")
table_frame = Frame(window)
table_frame.pack(fill=BOTH, expand=1, side="right")
select_frame = Frame(window)
select_frame.pack(side="left")
make_table(df)

window.mainloop()
"""