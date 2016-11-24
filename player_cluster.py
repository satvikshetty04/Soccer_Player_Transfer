import sqlite3
import pandas as pd
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler
from bokeh.plotting import figure, ColumnDataSource, show
from bokeh.models import HoverTool
import matplotlib.pyplot as plt
import seaborn as sns
import sys

# % matplotlib inline
# output_notebook()

database = './data/database.sqlite'
conn = sqlite3.connect(database)

query = """SELECT * FROM Player_Attributes a
           INNER JOIN (SELECT player_name, player_api_id AS p_id FROM Player) b ON a.player_api_id = b.p_id;"""

drop_cols = ['id','date','preferred_foot',
             'attacking_work_rate','defensive_work_rate']

players = pd.read_sql(query, conn)
players['date'] = pd.to_datetime(players['date'])
players = players[players.date > pd.datetime(2015,1,1)]
players = players[~players.overall_rating.isnull()].sort('date', ascending=False)
players = players.drop_duplicates(cols='player_api_id')
players = players.drop(drop_cols, axis=1)

# players.info()

players = players.fillna(0)

cols = ['player_api_id','player_name','overall_rating','potential']
stats_cols = [col for col in players.columns if col not in (cols)]

ss = StandardScaler()
tmp = ss.fit_transform(players[stats_cols])
model = TSNE(n_components=2, random_state=0)
tsne_comp = model.fit_transform(tmp)



tmp = players[cols]
tmp['comp1'], tmp['comp2'] = tsne_comp[:,0], tsne_comp[:,1]
tmp = tmp[tmp.overall_rating >= 80]

_tools = 'box_zoom,pan,save,resize,reset,tap,wheel_zoom'
fig = figure(tools=_tools, title='t-SNE of Players (FIFA stats)', responsive=True,
             x_axis_label='Component 1', y_axis_label='Component 2')

source = ColumnDataSource(tmp)
hover = HoverTool()
hover.tooltips=[('Jogador','@player_name'),]
fig.scatter(tmp['comp1'], tmp['comp2'], source=source, size=8, alpha=0.6,
            line_color='red', fill_color='red')

fig.add_tools(hover)

show(fig)
