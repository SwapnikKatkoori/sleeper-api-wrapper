from sleeper_wrapper import Players
import time
players = Players()

start = time.time()
all_players = players.get_all_players()
end = time.time()
print(end - start)

start = time.time()
all_players = players.get_all_players()
end = time.time()
print(end - start)