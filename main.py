"""from sleeper_wrapper import League, Players, Stats
import time
import pandas as pd"""
from tkinter import *
from tkinter import ttk
from pandastable import Table




"""
league_id = 650057741137690624
league = League(league_id)
league.get_league()
players = Players()
# all_players = players.get_all_players()
stats = Stats()

"""
root = Tk()
frm = ttk.Frame(root, padding=300)
frm.grid()

ttk.Label(frm, text="Hello World!").grid(column=0, row=0)
ttk.Menubutton(frm, text="Menubutton").grid(column=2, row=1)
ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=0)
root.mainloop()