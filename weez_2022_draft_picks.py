from sleeper_wrapper import League, Drafts
from draftboard_brain import get_draft_order, make_pick_list
draft_id = 850087629952249857
league_id = 850087629952249856

league = League(league_id)
draft = Drafts(draft_id)

picks = draft.get_all_picks()

traded = draft.get_traded_picks()

# print(picks)

for t in traded:
    print(t)



draft_order = get_draft_order(league)
# print(type(draft_order))
print(draft_order)
draft_order = [f"{k}: {v}" for k, v in draft_order.items()]
# print(sorted(draft_order))
# print(draft)
print(traded)
# print(picks)
this_draft = draft.get_specific_draft()

d_order = this_draft["draft_order"]
slots_to_roster_id = this_draft["slot_to_roster_id"]
pick_list = make_pick_list()

# print(d_order)
# print(slots_to_roster_id)
# print(pick_list)
pick_list_tuples = [tuple(map(int, p.split('.'))) for p in pick_list]
for t in pick_list_tuples:
    pass
    # print(t)
# print(pick_list_tuples)
# print(pick_list_tuples[5][1])
# p_match = [p[1] for p in pick_list_tuples]
# print(p_match)
