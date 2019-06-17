[![Build Status](https://travis-ci.org/SwapnikKatkoori/sleeper_wrapper.svg?branch=master)](https://travis-ci.org/SwapnikKatkoori/sleeper_wrapper)
![GitHub](https://img.shields.io/github/license/SwapnikKatkoori/sleeper_wrapper.svg?color=blue)
![GitHub issues](https://img.shields.io/github/issues/SwapnikKatkoori/sleeper_wrapper.svg?color=orange)
# sleeper_wrapper
A Python API wrapper for Sleeper Fantasy Football, as well as tools to simplify data recieved. It makes all endpoints found in the sleeper api docs: https://docs.sleeper.app/ available and turns the JSON recieved into python types for easy usage.


# Table of Contents

1. [ Installation ](#install)

2. [Usage](#usage)
    
    * [League](#league)
    
    * [User](#user)
    
    * [Stats](#stats)
    
    * [Players](#players)
3. [Notes](#notes)

<a name="install"></a>
# Install


<a name="usage"></a>
# Usage
There are five objects that get data from the Sleeper API specified below. Most of them are intuative based on the Sleeper Api docs.  

<a name="league"></a>

### League

#### Initiaize
```
from sleeper_wrapper import League

league = League(league_id)
```
- league_id: (str)The id of your sleeper league

#### League.get_league()
Gets data for the league that was specified when the League object was initialized. Data returned looks like: https://docs.sleeper.app/#get-a-specific-league

#### League.get_rosters()
Gets all of the rosters in the league. Data returned looks like: https://docs.sleeper.app/#getting-rosters-in-a-league 

#### League.get_users()
Gets all of the users in the league. Data returned looks like: https://docs.sleeper.app/#getting-users-in-a-league

#### League.get_matchups(week)
Gets all of the users in the league. Data returned looks like: https://docs.sleeper.app/#getting-matchups-in-a-league

- week:(int or string) week of the matchups to be returned.

#### League.get_playoff_winners_bracket()
Gets the playoff winners bracket for the league. Data returned looks like: https://docs.sleeper.app/#getting-the-playoff-bracket

#### League.get_playoff_losers_bracket()
Gets the playoff losers bracket for the league. Data returned looks like: https://docs.sleeper.app/#getting-the-playoff-bracket

#### League.get_transactions(week)
Gets all of the transactions data in the league. Data returned looks like: https://docs.sleeper.app/#get-transactions

- week:(int or str) week of the matchups to be returned.

#### League.get_traded_picks()
Gets all of the traded picks in the league. Data returned looks like: https://docs.sleeper.app/#get-traded-picks

#### League.get_all_drafts()
Gets all of the draft data in the league. Data returned looks like: https://docs.sleeper.app/#get-all-drafts-for-a-league

#### League.get_standings(rosters, users)
Gets the standings in a league. Returns a list of the standings in order of most wins to least wins.
- rosters: (list)The data returned by the get_rosters() method.
- users: (list)The data returned by the get_standings() method.
Data returned looks like: 
```
[("username", "number_of_wins", "total_points"), ("username", "number_of_wins", "total_points"),...]
```

#### League.get_scoreboards(rosters, matchups, users)
Gets the scoreboards of the league. Returns a dict of league mathups and scores.
- rosters: (list)The data returned by the get_rosters() method.
- matchups: (list)The data returned by the get_mathcups() method.
- users: (list)The data returned by the get_standings() method.
Data returned looks like: 

```
{matchup_id:[(team_name,score), (team_name, score)], matchup_id:[(team_name,score), (team_name, score)], ... }
```

#### League.get_close_games(scoreboards, close_num)
Gets all of the close games in a league. Returns a dict.
- scoreboards: (dict)The data returned by the get_scoreboards() method.
- close_num: (int)How close the games need to be considered a close game. For example, if the close num is 5, the data returned would only include matchups that are within 5 points of each other.

Data returned looks like: 

```
{matchup_id:[(team_name,score), (team_name, score)], matchup_id:[(team_name,score), (team_name, score)], ... } 
```
<a name="user"></a>
### User

<a name="stats"></a>
### Stats

<a name="players"></a>
### Players

<a name="notes"></a>
# Notes 
This package is intended to be used by Python version 3.5 and higher. There might be some wacky results for previous versions.
