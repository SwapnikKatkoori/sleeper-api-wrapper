from ecr import get_player_pool
import numpy as np
pp = get_player_pool()

# db = pp[["cheatsheet_text", 'is_keeper']][:9].to_numpy()
# db = PP["button_text"][:9].to_numpy()

# print(db)

print(pp.iloc[0, :])

pp['is_keeper'] = None
pp['draft_pick'] = None
pp['round'] = None
pp['draft_slot'] = None

pp = pp.loc[:8, ["cheatsheet_text", "sleeper_id", "is_keeper", "draft_pick", "round", "draft_slot"]]
pp.at[0, "draft_pick"] = 8
db = np.array(pp.to_dict("records"))
# db = PP["button_text"][:9].to_numpy()
db = db.reshape((3, 3))
# print(db)
print(db[0, 0]['is_keeper'])
db[0, 0]['is_keeper'] = True
db[0, 0]['round'] = 2
db[0, 0]['draft_slot'] = 2
# db[0, 0]['draft_pick'] = 8
# db[0, 0] = np.roll
print(db[0, 0])
k = db[0, 0]
print(type(k))

arr = np.full((3, 3), {"button_text": "-", "position": "-"})
print(arr)
arr[(k["round"], k["draft_slot"])] = k
print(arr)







"""[{'round': 1,
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
    ...]"""
"""
{'round': 12, 'roster_id': None, 'player_id': '4152', 'picked_by': '', 'pick_no': 142, 
'metadata': {'years_exp': '5', 'team': 'HOU', 'status': 'Active', 'sport': 'nfl', 'position': 'RB', 'player_id': '4152', 'number': '2', 'news_updated': '1655908847965', 'last_name': 'Mack', 'injury_status': '', 'first_name': 'Marlon'}, 
'is_keeper': None, 'draft_slot': 3, 'draft_id': '856772332067360768'}"""