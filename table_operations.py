from aenir2.data_dict import read_stat_names
from aenir2.name_lists import *
import pandas as pd
from os.path import sep

def zero_filler(game,file,row_data):
    if row_data is None:
        return
    row_data=row_data.to_dict()
    num_stats=read_stat_names(game)
    stats=stat_names(game)
    #   Consolidate names here
    for x in stats:
        #   Fill zeros here
        if x not in row_data.keys():
            row_data[x]=0
    for cell,stat in row_data.items():
        #   Resolve multi-promotion class errors
        if type(stat) == dict:
            for key,val in stat.items():
                row_data[cell]=val
    ordered_data={}
    #   Order stats here
    for stat in stats:
        ordered_data[stat]=row_data[stat]
    if file == 'classes_maximum-stats.csv':
        if game == '6':
            ordered_data['HP']=60
            ordered_data['Lck']=30
            ordered_data['Mov']=15
        if game == '9':
            ordered_data['Mov']=99
            ordered_data['Con']=99
            ordered_data['Wt']=99
    data=pd.Series(ordered_data)
    return data


def add_column(game,filename,data):
    if (game,filename) == ('7','classes_promotion-gains.csv'):
        #   SF page for FE7 does not have column for unpromoted classes
        promo_file='.','metadata',r'fe7_promo.csv'
        promo_file=sep.join(promo_file)
        unpromoted=()
        with open(promo_file) as r_file:
            index=0
            for line in r_file.readlines():
                line=line.strip()
                line=line.split(',')
                unpromoted+=(line[0],)
                #   Just to match correct classes to each other
                assert line[1] == data.index[index]
                index+=1
        promoted=tuple(data.index)
        data.index=unpromoted
        data.insert(loc=0,column='Promotion',value=promoted)
        data.rename_axis(axis=0,mapper='Class',inplace=True)
