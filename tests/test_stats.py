from sleeper_wrapper import Stats
import pytest

def test_get_all_stats(capsys):
	stats = Stats()
	all_stats = stats.get_all_stats('regular', 2018)
	assert isinstance(all_stats, dict)

def test_get_week_stats():
	stats = Stats()
	week_stats = stats.get_week_stats('regular', 2018, '2')
	assert isinstance(week_stats, dict)

def test_get_all_projections():
	stats = Stats()
	projections = stats.get_all_projections("regular", "2019")
	assert isinstance(projections, dict)

def test_get_week_projections():
	stats = Stats()
	week_projections = stats.get_week_projections("regular", 2018, "4")
	assert isinstance(week_projections, dict)

def test_get_player_week_score(capsys):
	stats = Stats()
	score = stats.get_player_week_score("regular","GB",2018, 5)

	assert isinstance(score, dict)
	assert score["pts_ppr"] == "Not Available"

	score = stats.get_player_week_score("regular", "1262",2018, 5)
	assert isinstance(score, dict)
	assert score["pts_ppr"] == "Not Available"

	score = stats.get_player_week_score("regular", "5170",2018, 5)

	assert isinstance(score, dict)
	assert score["pts_ppr"] != "Not Available"

	
	score = stats.get_player_week_score("regular","30000000",2018, 5)
	assert score is None

def test_get_player_week_stats():
	stats = Stats()
	week_stats = stats.get_player_week_stats("regular", "1262", 2018, 5)

	assert isinstance(week_stats, dict)

	week_stats = stats.get_player_week_stats("regular", "3000000", 2018, 5)
	assert week_stats is None
