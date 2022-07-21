"""
Cleanup projections from fantasypros
"""
import pdb
import re
import pandas as pd
from pathlib import Path
from sleeper_wrapper import League
import json

league = League()

class Projections:
    def __init__(self, scoring_keys=league.scoring_settings):
        self.qb_path = Path("data/projections/fpros/FantasyPros_Fantasy_Football_Projections_QB.csv")
        self.flex_path = Path("data/projections/fpros/FantasyPros_Fantasy_Football_Projections_FLX.csv")
        self.scoring_keys = scoring_keys
        self.qb_df = self.clean_qb_df()
        self.flex_df, self.rb_df, self.wr_df, self.te_df = self.clean_flex_df()
        self.all_df = self.get_all_df()
        self.dict = self.all_df.to_dict("records")

    def get_all_df(self):
        all_df = pd.concat([self.qb_df, self.rb_df, self.wr_df, self.te_df]).fillna(0)
        all_df = self.sort_reset_index(all_df)
        all_df.sort_values(by="vbd", ascending=False, inplace=True)
        all_df.reset_index(drop=True, inplace=True)
        all_df["overall_rank"] = all_df.index + 1
        return all_df

    def sort_reset_index(self, df):
        """
        This gets called every time we add vbd to sort by vbd and reset the index
        """
        df.sort_values(by=["vbd", "fpts"], ascending=False, inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df

    def get_custom_score_row(self, row):
        score = 0
        for k, v in self.scoring_keys.items():
            try:
                score += self.scoring_keys[k] * row[k]
            except KeyError:
                pass
        return score

    def clean_qb_df(self):
        qb_df = pd.read_csv(self.qb_path, skiprows=[1])

        # lower case all column names
        qb_df.columns = qb_df.columns.str.lower()
        qb_df.rename(columns={"tds": "pass_td",
                              "ints": "pass_int",
                              "att": "pass_att",
                              "att.1": "rush_att",
                              "yds": "pass_yd",
                              "yds.1": "rush_yd",
                              "tds.1": "rush_td",
                              "fl": "fum_lost",
                              "player": "name"}, inplace=True)

        # remove non-numeric (commas) characters from the number fields
        qb_df.replace(',', '', regex=True, inplace=True)
        qb_df["pass_yd"] = qb_df["pass_yd"].apply(pd.to_numeric)

        # calculate custom score and sort
        qb_df["fpts"] = qb_df.apply(self.get_custom_score_row, axis=1)
        # add position field needed before we can send to add_vbd
        qb_df["position"] = "QB"
        # send to add_vbd
        qb_df = self.add_vbd(qb_df)
        # add position and rank columns
        qb_df["position_rank"] = qb_df.index + 1
        qb_df["pos_rank"] = "QB" + qb_df["position_rank"].astype(str)
        return qb_df

    def clean_flex_df(self):
        """
        Take the single Flex CSV, clean up the column names, add the position and bonus
        columns, get custom score, split into positional DataFrames, and add VBD
        """
        flex_df = pd.read_csv(self.flex_path, skiprows=[1])  # skips the first blank row
        flex_df.columns = flex_df.columns.str.lower()
        flex_df["position"] = flex_df["pos"].str[:2]
        flex_df["position_rank"] = flex_df["pos"].str[2:]
        flex_df["bonus_rec_te"] = flex_df["rec"].loc[flex_df["position"] == "TE"]
        flex_df["bonus_rec_te"] = flex_df['bonus_rec_te'].fillna(0)
        flex_df.rename(columns={"player": "name",
                                "pos": "pos_rank",
                                "att": "rush_att",
                                "tds": "rush_td",
                                "yds": "rush_yd",
                                "yds.1": "rec_yd",
                                "tds.1": "rec_td",
                                "team": "team",
                                "fpts": "fpts",
                                "rec": "rec",
                                "fl": "fum_lost"}, inplace=True)

        # remove non numeric characters from the number fields
        flex_df.replace(',', '', regex=True, inplace=True)
        flex_df["rec_yd"] = flex_df["rec_yd"].apply(pd.to_numeric)
        flex_df["rush_yd"] = flex_df["rush_yd"].apply(pd.to_numeric)

        # calculate custom score and sort
        flex_df["fpts"] = flex_df.apply(self.get_custom_score_row, axis=1)
        flex_df.sort_values(by="fpts", inplace=True, ascending=False)

        # split into RB, WR, and TE DFs, return all 4
        rb_df = flex_df[flex_df["position"] == "RB"]
        rb_df = self.add_vbd(rb_df)
        wr_df = flex_df[flex_df["position"] == "WR"]
        wr_df = self.add_vbd(wr_df)
        te_df = flex_df[flex_df["position"] == "TE"]
        te_df = self.add_vbd(te_df)

        return flex_df, rb_df, wr_df, te_df

    def add_vbd(self, df):
        # get thresholds
        try:
            if df.iloc[1]['position'] == 'QB':
                vols_threshold = df.iloc[25]['fpts']
                vorp_threshold = df.iloc[31]['fpts']
            elif df.iloc[1]['position'] == 'RB':
                vols_threshold = df.iloc[33]['fpts']
                vorp_threshold = df.iloc[55]['fpts']
            elif df.iloc[1]['position'] == 'WR':
                vols_threshold = df.iloc[27]['fpts']
                vorp_threshold = df.iloc[63]['fpts']
            elif df.iloc[1]['position'] == 'TE':
                vols_threshold = df.iloc[10]['fpts']
                vorp_threshold = df.iloc[22]['fpts']
        except KeyError:
            pdb.set_trace()

        df["vols"] = df.apply(lambda row: self.calc_vols(row, vols_threshold), axis=1)
        df["vorp"] = df.apply(lambda row: self.calc_vorp(row, vorp_threshold), axis=1)
        df["vbd"] = df.apply(lambda row: self.calc_vbd(row), axis=1)
        df['vona'] = df.fpts.diff(periods=-1)
        df = self.sort_reset_index(df)
        return df

    def calc_vols(self, row, vols_threshold):
        return max(0, row['fpts'] - vols_threshold)

    def calc_vorp(self, row, vorp_threshold):
        return max(0, row['fpts'] - vorp_threshold)

    def calc_vbd(self, row):
        return max(0, row['vols'] + row['vorp'])


"""

"""
# TODO - 1. Calculate Tiers, 2. Match up with Sleeper IDs

prj = Projections()
df = prj.all_df



'''
# ---------- From Clustering Jupyter notebook
draft_pool = 192

df = df[:draft_pool]

from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans
from matplotlib import pyplot as plt
import numpy as np
import seaborn as sns;

sns.set_style('whitegrid');

avgs = []
pd.set_option("display.max_columns", None)
# print(df.columns)
# pdb.set_trace()
"""
We are going iterate from k=4 -> k=34 and try to find the silhouette score for each value of K.
We are going to choose the K that results in the highest score.
"""
start = 4
stop = 35

for n_clusters in range(start, stop):
    """
    We are clustering our data with the Avg. column as our one feature.
    """

    X = df[['vbd']].values

    """
    sklearn.cluster.KMeans documentation

    Notice that the process for fitting the KMeans model is more or less equivalent to the process
    we went through with the LinearRegression model we pulled out from the linear_model module.

    https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html
    """

    model = KMeans(n_clusters=n_clusters)  # instantiate the model with hyperparameters

    model.fit(X)  # fit the model

    labels = model.predict(X)  # predict labels (assign clusters) to our data

    silhouette_avg = silhouette_score(X, labels)  # calculate the silhouette avg for our labels

    avgs.append(silhouette_avg)  # append it to a list for plotting later

"""
Plotting the results.
np.arange is very similar to Python's range function

numpy.arange documentation

https://numpy.org/doc/stable/reference/generated/numpy.arange.html
"""
plt.plot(np.arange(start, stop, 1), avgs);
plt.xlabel('Number of clusters');
plt.ylabel('Silhouette score');

"""
matplotlib.pyplot.xticks allows us to set the xticks manually.
https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.xticks.html
"""
# print(plt.xticks(np.arange(start, stop, 1)))

from sklearn.cluster import KMeans

# pd.set_option('display.max_rows', None)

X = df[['vbd']].values

k = 32 # this is the value we got back from doing the silhouette analysis above

model = KMeans(n_clusters=k)

print(model.fit(X))

labels = model.predict(X)

print(labels)

def assign_tiers(labels):
    unique_labels = []
    tiers = []

    for i in labels:
        if i not in unique_labels:
            unique_labels.append(i)

        tiers.append(
            len(set(unique_labels))
        )

    return tiers


tiers = assign_tiers(labels)

df['Tier'] = tiers

print(df.set_index('Tier').head(30))
'''
