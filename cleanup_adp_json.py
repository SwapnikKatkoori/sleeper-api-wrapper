from pathlib import Path
import json
import requests

results = requests.get(url="https://fantasyfootballcalculator.com/api/v1/adp/2qb?teams=12&year=2022&position=all")
file_path = Path("data/adp/adp.json")


with open(file_path, "w") as json_write:
    json.dump(results, json_write, indent=4)



