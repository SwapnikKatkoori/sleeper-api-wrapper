# sleeper-api-wrapper
A Python API wrapper for Sleeper Fantasy Football, as well as tools to simplify data recieved. It makes all endpoints found in the sleeper api docs: https://docs.sleeper.app/ available.


# Table of Contents

1. [ Installation ](#install)

2. [Usage](#usage)
    
    * [League](#league)
    
    * [User](#user)
    
    * [Stats](#stats)
    
    * [Players](#players)

<a name="install"></a>
# Install


<a name="usage"></a>
# Usage
There are five objects that get data from the Sleeper API specified below. Most of them are intuative based on the Sleeper Api docs.  

<a name="league"></a>
## League
### get_league()
Gets data for the league that was specified when the League object was initialized. 
