import sqlite3
import pandas as pd
import sys
from pprint import pprint

database = './data/database.sqlite'
conn = sqlite3.connect(database)
cur = conn.cursor()
teams = []
players = {}

player_skills = {
    1: 'finishing, dribbling, volleys, heading_accuracy, curve, acceleration, sprint_speed, free_kick_accuracy, ball_control, short_passing, penalties, shot_power, balance, jumping',
    2: 'vision, ball_control, short_passing, long_passing, long_shots, marking, penalties, potential, aggression, sliding_tackle, standing_tackle',
    3: 'marking, standing_tackle, sliding_tackle, short_passing, long_passing, crossing, jumping, stamina, strength, long_shots, aggression, interceptions, positioning'
}

skill_count = {
    1: 14,
    2: 11,
    3: 13
}

def get_field_position(player_id):
    if player_id % 3 == 0:
        return 1
    elif player_id % 3 == 1:
        return 2
    else:
        return 3

def get_player_stats(player_id, field_pos):
    result = cur.execute( "Select " + player_skills[field_pos] + " from Player_Attributes where player_api_id =" + str(
            player_id) + "  and date between ('2013-07-01') and ('2014-06-30') order by date desc LIMIT 1;")
    player_stat = 0

    for row in result:
        for skill in row:
            player_stat += int(skill)

    return player_stat/skill_count[field_pos]

def main():
    result = cur.execute("SELECT DISTINCT team_api_id from PlayerTeamMod;")
    count = 0
    for team in result:
        count += 1
        if count > 10:
            break
        teams.append(team[0])
        players[team[0]] = {}

    for team in teams:
        result = cur.execute("SELECT player_api_id, team_api_id from PlayerTeamMod where team_api_id = " + str(team) + " AND season = '2013/2014' order by team_api_id;")
        player_list = []
        for row in result:
            player_list.append(row[0])

        for player_id in player_list:
            field_pos = get_field_position(player_id)
            player_stat = get_player_stats(player_id, field_pos)
            players[team][player_id] = [field_pos, player_stat]

    pprint(players)

main()
