from os.path import sep,exists
from os import walk
import pandas as pd
from aenir2.stat_table import *
from aenir2.gender_dict import promo_dict
from aenir2.match_names import *
from aenir2.name_lists import *
from aenir2.table_operations import *
from aenir2.child_stats import *


def load_unit_info(game,unit,father='Arden',lyn_mode=False):
    data_dir='.','raw_data','fe'+game
    data_dir=sep.join(data_dir)
    unit_info={}

    unit_info['Game']=game
    unit_info['Name']=unit

    if unit in fe4_child_list():
        unit_info['Father']=father

    if unit == 'Wallace':
        promo_status=not lyn_mode
    else:
        is_promo=promo_dict(game,is_promo=True)
        promo_status=is_promo[unit]
    unit_info['Promoted']=promo_status

    file_substr='characters_base-stats'

    if game == '7':
        if lyn_mode:
            suffix='1'
        else:
            suffix='2'
        file_substr+=suffix
        lyndis_league=character_list(
            game,\
            file_match='characters_base-stats1.csv'
            )
        if unit in lyndis_league:
            unit_info['Lyn Mode']=lyn_mode
    for root,folders,files in walk(data_dir):
        if root != data_dir:
            continue
        for file in files:
            if file_substr not in file:
                continue
            data_file=data_dir,file
            data_file=sep.join(data_file)
            data=pd.read_csv(data_file,index_col=0)
            if unit in data.index:                
                if 'Lv' in data.columns:
                    col='Lv'
                elif 'Level' in data.columns:
                    col='Level'
                unit_info['Class']=data.at[unit,'Class']
                unit_info['Level']=data.at[unit,col]
                #   Tell program to stop searching files once name is found
                break
    return unit_info


def get_class_name(game,unit,class_name,lyn_mode):
    if not class_name:
        unit_info=load_unit_info(game,unit,lyn_mode=lyn_mode)
        class_name=unit_info['Class']
        audit='bases'
    else:
        audit='promo'
    proper_name=lambda file: match_class_name(game,unit,class_name,file,audit=audit)
    return proper_name


def load_stats(game,name,file_match,exceptions=()):
    data_dir='.','raw_data','fe'+game
    data_dir=sep.join(data_dir)

    for root,folders,files in walk(data_dir):
        if root != data_dir:
            continue
        for file in files:
            if file_match not in file:
                continue
            if file in exceptions:
                continue
            data=read_stat_table(game,file)
            if callable(name):
                name=name(file)
            if name in data.index:
                row_data=data.loc[name,:]
                if file != 'classes_promotion-gains.csv':
                    x=zero_filler(game,file,row_data)
                else:
                    x=row_data
                return x
            else:
                continue


def load_character_bases(game,unit,lyn_mode=False,father='Arden'):
    file_match='characters_base-stats'
    exceptions=()
    if game == '4':
        #   For FE4 kids
        if unit in fe4_child_list():
            data=load_child_bases(unit,father)
            return data
        #   Back to main routine
        baldr_family='Celice','Leaf','Altenna'
        if unit not in baldr_family:
            exceptions+=('characters_base-stats3.csv',)
    elif game == '7':
        table_num=('1.csv' if not lyn_mode else '2.csv')
        exceptions+=('characters_base-stats'+table_num,)
    kwargs={
        'game':game,\
        'name':unit,\
        'file_match':file_match,\
        'exceptions':exceptions
        }
    data=load_stats(**kwargs)
    return data


def load_character_growths(game,unit,father='Arden',lyn_mode=None):
    file_match='characters_growth-rates'
    exceptions=()
    if game == '4':
        #   For FE4 kids
        if unit in fe4_child_list():
            data=load_child_growths(unit,father)
            return data
        #   Return to main routine if fails
        exceptions+=(
            'characters_growth-rates1.csv',\
            'characters_growth-rates4.csv'
            )
    kwargs={
        'game':game,\
        'name':unit,\
        'file_match':file_match,\
        'exceptions':exceptions
        }
    data=load_stats(**kwargs)
    return data


def load_class_maxes(game,unit,class_name='',lyn_mode=False,father=''):
    if game == '5':
        maxes_data='.','metadata','fe5_maxes.csv'
        maxes_data=sep.join(maxes_data)
        data=pd.read_csv(maxes_data,index_col=0,header=None,squeeze=True)
        return data
    file_match='classes_maximum-stats'
    proper_name=get_class_name(game,unit,class_name,lyn_mode)
    kwargs={
        'game':game,\
        'name':proper_name,\
        'file_match':file_match,
        }
    data=load_stats(**kwargs)
    return data


def load_class_promo(game,unit,class_name='',promo_path=0,lyn_mode=False,father=''):
    file_match='classes_promotion-gains.csv'
    proper_name=get_class_name(game,unit,class_name,lyn_mode)
    kwargs={
        'game':game,\
        'name':proper_name,\
        'file_match':file_match,
        }
    data=load_stats(**kwargs)
    if type(data) == pd.DataFrame:
        t=promo_dict(game)
        if unit in t.keys():
            promo_path=t[unit]
        assert 0 <= promo_path < len(data)
        data=data.iloc[promo_path,:]
    data=zero_filler(game,file_match,data)
    return data


def load_class_promo_dict(game,promo_path=0,unit='',lyn_mode=None,father=''):
    filename='classes_promotion-gains.csv'
    file='.','raw_data','fe'+game,filename
    file=sep.join(file)
    data=pd.read_csv(file,index_col=0)
    #   Exception for FE7 promo-table; does not have unpromoted classes column
    if game == '7':
        promoted=tuple(data.index)
    else:
        promoted=tuple(data.iloc[:,0])
    #   Add unpromoted classes and set as index
    add_column(game,filename,data)
    unpromoted=tuple(data.index)
    d={}
    count=0
    exclude_list=()
    for scrub,elite in zip(unpromoted,promoted):
        if scrub in exclude_list:
            continue
        if scrub in d.keys():
            count+=1
            if count == promo_path:
                d[scrub]=elite
                exclude_list+=(scrub,)
                count=0
        else:
            d[scrub]=elite
    return d


def load_class_promo_list(game,unit,lyn_mode=False,father='',class_name=''):
    if (game,unit,lyn_mode) == ('7','Wallace',False):
        return
    check_promo_status=promo_dict(game,is_promo=True)
    if check_promo_status[unit]:
        return
    filename='classes_promotion-gains.csv'
    file='.','raw_data','fe'+game,filename
    file=sep.join(file)
    data=pd.read_csv(file,index_col=0)
    add_column(game,filename,data)
    if not class_name:
        unit_info=load_unit_info(game,unit,lyn_mode=lyn_mode)
        class_name=unit_info['Class']
        audit='bases'
    else:
        audit='promo'
    name_in_promo=match_class_name(game,unit,class_name,filename,audit=audit)
    if name_in_promo is None:
        return
    #   Evaluates to None on subsequent promotions
    paths=promo_dict(game)
    class_data=data.loc[name_in_promo,:]
    d={}
    if type(class_data) == pd.DataFrame:
        if unit in paths.keys():
            promo_path=paths[unit]
            assert 0 <= promo_path < len(class_data)
            promo_col_loc=tuple(class_data.columns).index('Promotion')
            x=class_data.iat[promo_path,promo_col_loc]
            d[promo_path]=x
        else:
            x=class_data.iloc[:,0]
            for num,name in enumerate(x):
                d[num]=name
    else:
        d[0]=class_data['Promotion']
    if d:
        return d        


def load_class_growths(game,unit,class_name='',lyn_mode=False,father=''):
    if game not in ('6','7'):
        return
    file_match='classes_growth-rates'
    proper_name=get_class_name(game,unit,class_name,lyn_mode)
    kwargs={
        'game':game,\
        'name':proper_name,\
        'file_match':file_match,
        }
    data=load_stats(**kwargs)
    return data


if __name__=='__main__':
    x=4
