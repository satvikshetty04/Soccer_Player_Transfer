import sqlite3
import pandas as pd
import sys
from pprint import pprint

def get_field_position(player_id):
    if player_id % 3 == 0:
        return 1
    elif player_id % 3 == 1:
        return 2
    else
        return 3

database = './data/database.sqlite'
conn = sqlite3.connect(database)
cur = conn.cursor()
teams = []
players = {}
result = cur.execute("SELECT DISTINCT team_api_id from PlayerTeamMod;")

for team in result:
    teams.append(team[0])
    players[team[0]] = []

for team in teams:
    result = cur.execute("SELECT player_api_id from PlayerTeamS where team_api_id = " + str(team) + " AND season = '2013/2014';")

    for row in result:
        field_pos = get_field_position(row[0])
        players[team].append((row[0], field_pos))

pprint(players)
