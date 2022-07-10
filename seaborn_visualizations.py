import pandas as pd; pd.set_option('display.max_columns', None)
import seaborn as sns
from matplotlib import pyplot as plt
from scipy.spatial import distance
df = pd.read_csv('https://raw.githubusercontent.com/fantasydatapros/data/master/yearly/2019.csv').iloc[:, 1:]

df.head()


"""
View the documentation for the info method here

https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.info.html
"""

df.info(verbose=True)