import pandas as pd
import numpy as np
import csv
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns

def generate_data():
    customers = pd.read_csv('./customers.csv')
    orders = pd.read_csv('./orders.csv')

    orders['parsed_created_time'] = orders.created.apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
    reporting_date = datetime.strptime('2015-07-08', '%Y-%m-%d')
    orders['week_n'] = orders["parsed_created_time"] .apply(lambda x: - (x - reporting_date).days // 7)
    orders.sort_values(by="parsed_created_time", ascending=False)

    reporting_date = datetime.strptime('2015-07-08', '%Y-%m-%d')
    customers['parsed_created_time'] = customers.created.apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
    reporting_date = datetime.strptime('2015-07-08', '%Y-%m-%d')
    customers['week_n'] = customers["parsed_created_time"].apply(lambda x: - (x - reporting_date).days // 7)
    customers.sort_values(by="parsed_created_time", ascending=False)

    df = customers.merge(orders, how='inner', left_on='id', right_on='user_id').sort_values(by="parsed_created_time_x", ascending=False)[['week_n_x', 'week_n_y', 'id_x']]
    df.drop_duplicates()
    df['week_n_y'] = df['week_n_x'] - df['week_n_y']
    piv = df.groupby(['week_n_x', 'week_n_y']).agg({'id_x': np.count_nonzero})
    piv = piv.rename_axis(['cohort', 'weeks_since_registered'])
    unstacked_piv = piv.unstack()
    return unstacked_piv

def insert_total(unstacked_piv):
    total = unstacked_piv.sum(axis=1)
    unstacked_piv.insert(0, 'distinctive_customers', pd.Series(total))
    return unstacked_piv

def generate_image(dataTable):
    unstacked_piv = dataTable
    cols = list(unstacked_piv)
    unstacked_piv[cols] = unstacked_piv[cols].div(unstacked_piv[cols].sum(axis=1), axis=0).multiply(100)
    cols = list(unstacked_piv)
    print(unstacked_piv)
    unstacked_piv.columns = ["customers"] + [t[1] for t in cols[1:]]
    sns.set(style='white')
    plt.title('Cohorts:  purchases from distinct users ')
    ax = sns.heatmap(unstacked_piv, mask=unstacked_piv.isnull(), annot=False, xticklabels=False);
    fig = ax.get_figure()
    fig.savefig("tmp/heatmap.png")

def to_html():
    f = open("templates/data.html","w")
    data = generate_data()
    dataTable = insert_total(data.copy())
    str = "<html><head><title>Cohort Analysis</title><style>table {border-collapse: collapse;width: 100%;} tr:nth-child(even){background-color: #f2f2f2}</style><head><body><div>" + dataTable.to_html() + "</div><div><img src='/heatmap.png' /></div></body></html>"
    f.write(str)
    f.close()
    generate_image(data)
    return