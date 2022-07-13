from sleeper_wrapper import League, Stats, Drafts, User
import json
import pdb
import pandas as pd

# initiliaze League - creates new object of League class
# get_league, _rosters, and _users
league_id = 650057741137690624 # Weez League ID 2021
league = League(league_id)
weez_league = league.get_league() # pulls dict of league
weez_rosters = league.get_rosters()
weez_users = league.get_users()

# initalize drafts.  all_drafts is a list, but only 1 item.
# other years get different league and draft IDs, found in
# weez_league['previous_league_id']
all_drafts = league.get_all_drafts() # this only gets the current draft
weez_draft_id = all_drafts[0]['draft_id']  # 650057741137690625
draft = Drafts(weez_draft_id)
weez_draft = draft.get_all_picks()

with open('data/players/all_players.json') as json_file:
    all_players = json.load(json_file)


def get_previous_keepers():
    prev_league_init = League(weez_league["previous_league_id"])
    prev_league = prev_league_init.get_league()
    prev_draft_id = prev_league['draft_id']
    prev_draft = Drafts(prev_draft_id)
    prev_draft_picks = prev_draft.get_all_picks()
    keeper_list = []

    for pick in prev_draft_picks:
        if pick['is_keeper'] == True:
            keeper_list.append(pick)

    return (keeper_list)


def check_keeper(player_id, keep_count):
    # might pass in league_id to figure out previous 2 years

    prev_keeper_list = get_previous_keepers()

    # run player_id through previous drafts

    for draft_pick in prev_keeper_list:
        if player_id == draft_pick['player_id']:
            keeper = draft_pick['is_keeper']
            if keeper == True:
                # pdb.set_trace()
                keep_count += 1

    return keep_count


def get_player_name(player_id):
    player_name = str(all_players[player_id]['first_name'] + " " + all_players[player_id]['last_name'])
    return player_name


def get_draft_rounds(player_id):
    player_dict = {}
    player_name = str(all_players[player_id]['first_name'] + " " + all_players[player_id]['last_name'])
    draft_round_2021 = 'Undrafted'
    draft_value_2022 = 16
    team = all_players[player_id]['team']
    position = all_players[player_id]['position']
    keeper = False
    keep_count = 0

    for draft_pick in weez_draft:

        if player_id == draft_pick['player_id']:
            draft_round_2021 = draft_pick['round']
            keeper = draft_pick['is_keeper']

            if keeper == True:
                current_keep_count = 1
                prev_keep_count = check_keeper(player_id, keep_count)
                keep_count = current_keep_count + prev_keep_count

            if draft_pick['round'] < 3:
                draft_value_2022 = 'Cannot Keep (drafted in top 3 rounds)'
            elif keep_count >= 2:
                draft_value_2022 = 'Cannot Keep (kept for 2 consecutive years). '
            else:
                draft_value_2022 = draft_pick['round'] - 2

    player_dict.update(player_name=player_name, position=position, team=team, draft_round_2021=draft_round_2021,
                       draft_value_2022=draft_value_2022, keeper=keeper, keeper_count=keep_count)

    return (player_dict)


for roster in weez_rosters:
    keeper_roster = dict()
    keeper_roster['owner_id'] = roster['owner_id']
    keeper_players = [get_draft_rounds(player) for player in roster['players']]

    keeper_roster['players'] = keeper_players

    keeper_players.append(keeper_roster)

print(keeper_roster)