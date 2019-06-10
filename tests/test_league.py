from sleeper_api import League 

def test_get_league():
	""" Tests the get_league method"""
	league = League(355526480094113792)
	league_info = league.get_league()
	assert isinstance(league_info, dict)
	assert league_info["league_id"] == "355526480094113792"

def test_get_rosters():
	""" Tests the get_league method"""
	league = League(355526480094113792)
	rosters = league.get_rosters()
	assert isinstance(rosters, list) 
	assert len(rosters)>5

def test_get_users():
	""" Tests the get_league method"""
	league = League(355526480094113792)
	users = league.get_users()

	assert isinstance(users, list)
	assert isinstance(users[0]["user_id"], str)
	#I guess username is not a thing

def test_get_matchups():
	""" Tests the get_league method"""
	league = League(355526480094113792)
	matchup_info = league.get_matchups(4)
	first_item = matchup_info[0]
	assert isinstance(matchup_info, list)
	assert isinstance(first_item, dict)

	matchup_info = league.get_matchups("4")
	assert isinstance(matchup_info, list)

def test_get_playoff_winners_bracket():
	""" Tests the get_league method"""
	league = League(355526480094113792)
	bracket = league.get_playoff_winners_bracket()
	first_item = bracket[0]
	assert isinstance(bracket, list)
	assert isinstance(first_item, dict)

def test_get_playoff_losers_bracket():
	""" Tests the get_league method"""
	league = League(355526480094113792)
	bracket = league.get_playoff_losers_bracket()
	first_item = bracket[0]
	assert isinstance(bracket, list)
	assert isinstance(first_item, dict)

def test_get_transactions():
	""" Tests the get_league method
	Note: Not realy sure wether this method works or what its supposed to do
	"""
	league = League(355526480094113792)
	transactions = league.get_transactions(4)
	assert isinstance(transactions, list)

	transactions = league.get_transactions("4")
	assert isinstance(transactions, list)

def test_get_traded_picks():
	""" Tests the get_league method"""
	league = League(355526480094113792)
	traded_picks = league.get_traded_picks()
	first_item = traded_picks[0]
	assert isinstance(traded_picks, list)
	assert isinstance(first_item, dict)

def test_get_standings():
	""" Tests the get_league method"""
	pass

def test_get_highest_scorer():
	""" Tests the get_highest_scorer() method"""
	pass