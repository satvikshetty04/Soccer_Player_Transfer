import sqlite3
import pandas as pd
from sklearn.manifold import TSNE
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

query = "SELECT name FROM sqlite_master WHERE type='table';"
pd.read_sql(query, conn)


query = "SELECT * FROM Player;"
a = pd.read_sql(query, conn)
a.head()

query = "SELECT * FROM Player_Attributes;"
a = pd.read_sql(query, conn)
a.head()

query = """SELECT * FROM Player_Attributes a
           INNER JOIN (SELECT player_name, player_api_id AS p_id FROM Player) b ON a.player_api_id = b.p_id;"""

drop_cols = ['id','date','preferred_foot',
             'attacking_work_rate','defensive_work_rate']

players = pd.read_sql(query, conn)
players['date'] = pd.to_datetime(players['date'])
players = players[players.date > pd.datetime(2015,1,1)]
players = players[~players.overall_rating.isnull()].sort('date', ascending=False)
players = players.drop_duplicates(subset='player_api_id')
players = players.drop(drop_cols, axis=1)

players.info()

players = players.fillna(0)

cols = ['player_api_id','player_name','overall_rating','potential']
stats_cols = [col for col in players.columns if col not in (cols)]
playerTsnePos = {}

def bookehPlottsne(tmp):
    _tools = 'box_zoom,pan,save,resize,reset,tap,wheel_zoom'
    fig = figure(tools=_tools, title='t-SNE of Players (FIFA stats)', responsive=True,
             x_axis_label='Component 1', y_axis_label='Component 2')
    source = ColumnDataSource(tmp)
    hover = HoverTool()
    hover.tooltips=[('Player','@player_name'),]
    fig.scatter(tmp['comp1'], tmp['comp2'], source=source, size=8, alpha=0.6,
            line_color='red', fill_color='red')

    fig.add_tools(hover)

    show(fig)
    return True


def tsneDimReduction(val): 
    ss = StandardScaler()
    tmp = ss.fit_transform(players[stats_cols])
    model = TSNE(n_components=2, random_state=0)
    tsne_comp = model.fit_transform(tmp)
    
    i = 0
    for player_id in players['player_api_id']:
        playerTsnePos[player_id] = (tsne_comp[:,0][i], tsne_comp[:,1][i])
        i += 1
    tmp = players[cols]
    tmp['comp1'], tmp['comp2'] = tsne_comp[:,0], tsne_comp[:,1]
    tmp = tmp[tmp.overall_rating >= val]
    X = (tmp['comp1'], tmp['comp2'])

    X2 = np.array(tmp['comp1'])
    X2.ndim
    X2.shape
    Y2 = np.array(tmp['comp2'])
    Y2.ndim
    Y2.shape

    X1 = np.vstack((X2,Y2)).T
    X1.ndim
    X1.shape
    return tmp, X1

def playerPredict(player_id):
    X2 = np.array(playerTsnePos[player_id][0])
    X2.ndim
    X2.shape
    Y2 = np.array(playerTsnePos[player_id][1])
    Y2.ndim
    Y2.shape

    Xz = np.vstack((X2,Y2)).T
    Xz.ndim
    Xz.shape
    
    print(kmeans1.predict(Xz))

def clusteringKMeans(XVal): 
    kmeans = KMeans(n_clusters=4, random_state=0)
    kmeans.fit(XVal)
    centroids = kmeans.cluster_centers_
    labels = kmeans.labels_
    print(centroids)
    colors = ["g.","r.","y.","c.","b."]

    for i in range(len(XVal)):
        plt.plot(XVal[i][0],XVal[i][1],colors[labels[i]], markersize = 10)
    plt.scatter(centroids[:, 0], centroids[:, 1], marker="x", s=150, linewidth = 5, zorder = 10)
    return kmeans, plt, labels


tmp, X10 = tsneDimReduction(80)
kmeans1, plt, labels = clusteringKMeans(X10)

def count_sort(arr,k):
    n = k + 1
    c = [0] * n

    for j in arr:
        c[j] = c[j] + 1

    return c

#count_sort(labels,3)

#plt.show()