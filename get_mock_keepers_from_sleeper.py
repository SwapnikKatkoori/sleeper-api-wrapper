from sleeper_wrapper import Drafts
import json
from pathlib import Path

def get_mock_keepers(mock_id=855693188285992960):
    mock_draft = Drafts(mock_id)

    return mock_draft.get_all_picks()


mp = get_mock_keepers()
for p in mp:
    if 'player_id' in p.keys():
        p['sleeper_id'] = p['player_id']
    p['is_keeper'] = True

print(mp)
path = Path('data/keepers/keepers.json')
with open(path, "w") as file:
    json.dump(mp, file, indent=4)