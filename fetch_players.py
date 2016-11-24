import sqlite3
import pandas as pd
import sys

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
        players[team].append(row[0])

print players
