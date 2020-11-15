from os.path import sep
import pandas as pd
from aenir2.data_dict import read_stat_names
from aenir2.table_operations import add_column

def read_stat_table(game,filename):
    file='.','raw_data','fe'+game,filename
    file=sep.join(file)
    df=pd.read_csv(file,index_col=0)
    num_stats=read_stat_names(game)
    stat_names=()
    for stat in num_stats.keys():
        if stat not in df.columns:
            continue
        stat_names+=(stat,)
    data=df.loc[:,stat_names]
    new_stat_names=()
    for stat in stat_names:
        if num_stats[stat]:
            x=num_stats[stat]
        else:
            x=stat
        new_stat_names+=(x,)
    data.columns=new_stat_names
    add_column(game,filename,data)
    return data
