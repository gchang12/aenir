from aenir2.name_lists import fe4_child_list,get_stat_names
from os.path import sep
import pandas as pd
from aenir2.data_dict import read_stat_names


def load_child_attributes(unit,filename,father):
    #   Bases: characters_base-stats3.csv
    #   -   Exclude Celice, Leaf, Altenna
    #   Growths: characters_growth-rates4.csv
    kid_list=fe4_child_list()
    dad_list=fe4_child_list(get_father=True)
    #   Check if valid pair
    if unit not in kid_list:
        return
    elif father not in dad_list:
        return
    data_src='.','raw_data','fe4',filename
    data_src=sep.join(data_src)
    data=pd.read_csv(data_src)
    kwargs={
        'game':'4',
        'file_match':filename
        }
    #   Generate list to find index of father
    unit_list=tuple(data.iloc[:,0])
    unit_row_loc=unit_list.index(unit)
    father_column_loc=tuple(data.columns).index('Father')
    #   Will always be 'Arden'
    arden=data.iat[unit_row_loc,father_column_loc]
    #   Temporary row for unit with Arden as father
    unit_stats=data.iloc[unit_row_loc,:]
    if father == arden:
        return unit_stats
    #   Begin looking for father by searching through list
    get_pos=False
    for num,name in enumerate(unit_list):
        if name == father:
            #   Does not get turned on until unit is found
            if not get_pos:
                continue
            father_row_loc=num
            break
        #   If found unit, then start searching for row with father
        if name == unit:
            get_pos=True
    #   Length of the rows subtracted by father index
    stop=len(data.columns)-father_column_loc
    #   Isolate row with father up until last numerical stat
    stats_slice=data.iloc[father_row_loc,:stop]
    corrected_stats=unit_stats[:father_column_loc],stats_slice
    #   Merge and rename row
    df=pd.concat(corrected_stats)
    df.index=data.columns
    return df


def load_child_stats(unit,filename,father):
    df=load_child_attributes(unit,filename,father)
    num_stats=read_stat_names('4')
    old_stat_names=list(num_stats.keys())
    data=df.loc[old_stat_names]
    new_stat_names=stat_names(game='4')
    data.index=new_stat_names
    return pd.Series(data,dtype='int64')


def load_child_bases(unit,father):
    filename='characters_base-stats3.csv'
    args=unit,filename,father
    return load_child_stats(*args)


def load_child_growths(unit,father):
    filename='characters_growth-rates4.csv'
    args=unit,filename,father
    return load_child_stats(*args)
