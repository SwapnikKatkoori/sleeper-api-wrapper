from sleeper_wrapper import League, Drafts
from draftboard_brain import get_draft_order
draft_id = 850087629952249857
league_id = 850087629952249856

league = League(league_id)
draft = Drafts(draft_id)

picks = draft.get_all_picks()

traded = draft.get_traded_picks()

print(picks)

# print(traded)

for p in traded:
    print(p)


draft_order = get_draft_order(league)
print(type(draft_order))
print(draft_order)