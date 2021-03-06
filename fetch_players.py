import sqlite3
import pandas as pd
import sys
from pprint import pprint
import soccerAnalysis1
import sqlite3
import pandas as pd
from sklearn.manifold import TSNE
from scipy.spatial import distance
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.datasets.samples_generator import make_blobs
from sklearn.preprocessing import StandardScaler
from bokeh.plotting import figure, ColumnDataSource, show
from bokeh.models import HoverTool
import numpy as np
from pylab import plot,show
from numpy import vstack,array
from numpy.random import rand
from scipy.cluster.vq import kmeans,vq
from mpl_toolkits.mplot3d import Axes3D
from bokeh.io import output_notebook
import matplotlib.pyplot as plt
import seaborn as sns

database = './data/database.sqlite'
conn = sqlite3.connect(database)
cur = conn.cursor()
teams = []
players = {}

#   1 : attack
#   2 : defense
#   3 : midfield

player_skills = {
    0: 'finishing, dribbling, volleys, heading_accuracy, curve, acceleration, sprint_speed, free_kick_accuracy, ball_control, short_passing, penalties, shot_power, balance, jumping',
    2: 'vision, ball_control, short_passing, long_passing, long_shots, marking, penalties, potential, aggression, sliding_tackle, standing_tackle',
    3: 'marking, standing_tackle, sliding_tackle, short_passing, long_passing, crossing, jumping, stamina, strength, long_shots, aggression, interceptions, positioning'
}

skill_count = {
    0: 14,
    2: 11,
    3: 13
}

def get_field_position(player_id):
    if player_id % 3 == 0:
        return 0
    elif player_id % 3 == 1:
        return 2
    else:
        return 3

def getYoungerPlayer(team_id, season):
    cur.execute("SELECT DISTINCT PT.player_api_id, PT.team_api_id from PlayerTeamMod PT, Player P where PT.team_api_id = " + str(team_id) + " AND PT.season = " + str("'" + season + "'") +" AND " + "(SELECT (strftime('%Y', 'now') - strftime('%Y', birthday)) - (strftime('%m-%d', 'now') < strftime('%m-%d', birthday)) from Player where player_api_id = PT.player_api_id) < 21" + " order by PT.team_api_id;")
    allrows = cur.fetchall()
    print(allrows)

def getOldestPlayer(team_id, season):
    cur.execute("SELECT DISTINCT PT.player_api_id, PT.team_api_id from PlayerTeamMod PT, Player P where PT.team_api_id = " + str(team_id) + " AND PT.season = " + str("'" + season + "'") +" AND " + "(SELECT (strftime('%Y', 'now') - strftime('%Y', birthday)) - (strftime('%m-%d', 'now') < strftime('%m-%d', birthday)) from Player where player_api_id = PT.player_api_id) > 34" + " order by PT.team_api_id;")
    allrows = cur.fetchall()
    print(allrows)

def get_player_stats(player_id, field_pos):
    result = cur.execute( "Select " + player_skills[field_pos] + " from Player_Attributes where player_api_id =" + str(
            player_id) + "  and date between ('2013-07-01') and ('2014-06-30') order by date desc LIMIT 1;")
    player_stat = 0

    for row in result:
        for skill in row:
            player_stat += int(skill)

    return player_stat/skill_count[field_pos]

def get_weak_player(team):
    result = cur.execute("SELECT player_api_id from PlayerTeamMod where team_api_id = " + str(team) + " AND season = '2013/2014' order by team_api_id;")
    player_list = {}
    for row in result:
        player_list[row[0]] = []

    team_attack = 0
    team_defense = 0
    team_midfield = 0
    team_attack_count = 0
    team_defense_count = 0
    team_midfield_count = 0

    for player_id in player_list:
        field_pos = get_field_position(player_id)
        player_stat = get_player_stats(player_id, field_pos)
        player_list[player_id] = [field_pos, player_stat]

        if field_pos == 1:                               # attack
            team_attack += player_stat
            team_attack_count += 1
        elif field_pos == 2:                             # defense
            team_defense += player_stat
            team_defense_count += 1
        else:                                            # midfield
            team_midfield += player_stat
            team_midfield_count += 1

    team_attack /= team_attack_count
    team_defense /= team_defense_count
    team_midfield /= team_midfield_count

    if team_attack > team_midfield:
        min_field = 3
        min = team_midfield
    else:
        min_field = 1
        min = team_attack

    if team_defense < min:
        min_field = 2

    min_stat = 100
    for player_id in player_list:
        if player_list[player_id][0] == min_field and min_stat > player_list[player_id][1]:
            min_stat = player_list[player_id][1]
            min_player = player_id

    print (str(team) + " : " +str(min_player))
    return (min_player, player_list[min_player][0])

def main():
    result = cur.execute("SELECT DISTINCT team_api_id from PlayerTeamMod;")
    for team in result:
        teams.append(team[0])

    for team in teams:
        get_weak_player(team)

main()
