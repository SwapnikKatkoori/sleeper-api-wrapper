from pathlib import Path
import pandas as pd
from sleeper_wrapper import League
POS_LIST = ['QB', 'RB', 'WR', 'TE']

league = League()
scoring = league.scoring_settings

# for k, v in scoring.items():
#     print(k)


file_path = Path("data/projections/NFLDK2022_CS_ClayProjections2022.xlsx")
sheet = "QB"  # sheet name or sheet number or list of sheet numbers and names
df = pd.read_excel(io=file_path, sheet_name=sheet)

df.rename(columns={'Quarterback': 'Name', 'Pos Rk FF Pt': 'Pos_Rk', 'Unnamed: 4': 'FF_Pt'}, inplace=True)
df.rename(columns={'Ru Yds': 'rush_yd', 'Ru TD': 'rush_td', 'P TD': 'pass_td', 'P Yds': 'pass_yd'}, inplace=True)
# print(list(df.columns))

# for _, row in df.iterrows():
#     for k, v in scoring.items():
#         print(k, v*_)
#     print("________________")

for column in df.columns():
    try:
        df['pts_custom'] += df[column] * scoring[column]
    except TypeError:
        print(f"type error on column: {column}")
        pass
print(df.head())
# df['pts_custom'] = [newitem for item in list]
# vols = df.loc[23]
# print(vols)
