import os
import pandas as pd
from aenir2.data_dict import read_stat_names
from aenir2.gender_dict import gender_dict,promo_dict
from aenir2 import save_stats


def read_stat_table(game,filename):
    file='.','raw_data','fe'+game,filename
    file=os.path.sep.join(file)
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
    if (game,filename) == ('7','classes_promotion-gains.csv'):
        #   SF page for FE7 does not have column for unpromoted classes
        promo_file='.','metadata',r'fe7_promo.csv'
        promo_file=os.path.sep.join(promo_file)
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
    return data


def read_class_names2(game,audit_name,match_name):
    name_file=r'fe'+game+'.csv'
    table='.','metadata','class_names',name_file
    table=os.path.sep.join(table)
    s=()
    audit_match=[audit_name,match_name]
    with open(table) as r_file:
        for line in r_file.readlines():
            line=line.strip()
            line=line.split(',')
            s+=(line,)
    start=None
    stop=None
    for num,name in enumerate(s):
        if name == audit_match:
            start=num
        if not name[0] and start is not None:
            stop=num
            break
    if None in (start,stop):
        return {}
    else:
        return dict(s[start+1:stop])


def test_read_stats():
    k=4
    game=str(k)
    filename='characters_base-stats1'
    args=game,filename
    x=read_stat_table(*args)
    unit=x.loc['Sigurd',:].transpose()
    print(unit)


def match_class_name(game,unit,class_name,filename,audit='bases'):
    assert 'classes' in filename
    categories='bases',\
                'growths',\
                'maxes',\
                'promo'
    file_substrings='base-stats',\
                     'growth-rates',\
                     'maximum-stats',\
                     'promotion-gains'

    for substring in file_substrings:
        if substring in filename:
            code_loc=file_substrings.index(substring)
            code=categories[code_loc]
            break

    gender_for=gender_dict(game)
    suffix=gender_for[unit]
    x=read_stat_table(game,filename)
    match_list=x.index
    name_matches=read_class_names2(game,audit,code)

    #   Check if name without suffix appears in page
    if class_name in match_list:
        return class_name

    #   Check if name with gender-suffix appears
    elif class_name in name_matches.keys():
        proper_name=name_matches[class_name]
        if proper_name in match_list:
            return proper_name

    gendered_class=class_name+suffix

    #   Check if corrected version of name appears
    if gendered_class in name_matches.keys():
        proper_name=name_matches[gendered_class]
        if proper_name in match_list:
            return proper_name

    #   Check if gendered version of that name appears
    elif gendered_class in match_list:
        return gendered_class


def load_unit_attributes(game,unit,lyn_mode=False):
    data_dir='.','raw_data','fe'+game
    data_dir=os.path.sep.join(data_dir)
    attr={}
    if not os.path.exists(data_dir):
        save_stats(game)
    for root,folders,files in os.walk(data_dir):
        #   Skip metadata check
        if not folders:
            continue
        for file in files:
            if 'characters' not in file:
                continue
            #   List of bad tables
            if game == '4':
                #   Skip growths of Gen-1 units without Holy Blood bonus
                if file == 'characters_growth-rates1.csv':
                    continue
                #   Take only bases from these three
                baldr_family='Celice','Leaf','Altenna'
                if unit not in baldr_family:
                    if file == 'characters_base-stats3.csv':
                        continue
                #   Skip growth rates for variable kids
                if file == 'characters_growth-rates4.csv':
                    continue
            if game == '7':
                if lyn_mode:
                    #   Skip main unit list
                    if file == 'characters_base-stats2.csv':
                        continue
                else:
                    #   Skip Lyn Mode unit list
                    if file == 'characters_base-stats1.csv':
                        continue
            data=read_stat_table(game,file)
            if unit in data.index:
                key=('bases' if 'base-stats' in file else 'growths')
                attr[key]=data.loc[unit,:]
    return attr


def load_unit_info(game,unit,lyn_mode=False):
    data_dir='.','raw_data','fe'+game
    data_dir=os.path.sep.join(data_dir)
    unit_info={}
    file_substr='base-stats'
    if game == '7':
        if lyn_mode:
            suffix='1'
        else:
            suffix='2'
        file_substr+=suffix
    for root,folders,files in os.walk(data_dir):
        if not files:
            continue
        for file in files:
            if file_substr not in file:
                continue
            data_file=data_dir,file
            data_file=os.path.sep.join(data_file)
            data=pd.read_csv(data_file,index_col=0)
            if 'Lv' in data.columns:
                col='Lv'
            elif 'Level' in data.columns:
                col='Level'
            if unit in data.index:
                unit_info['Class']=data.at[unit,'Class']
                unit_info['Level']=data.at[unit,col]
    return unit_info


def load_class_attributes(game,unit,lyn_mode=False,promo_path=0):
    data_dir='.','raw_data','fe'+game
    data_dir=os.path.sep.join(data_dir)
    unit_info=load_unit_info(game,unit,lyn_mode=lyn_mode)
    unit_class=unit_info['Class']
    attr={}
    if not os.path.exists(data_dir):
        save_stats(game)
    for root,folders,files in os.walk(data_dir):
        #   Skip metadata check
        if not folders:
            continue
        for file in files:
            #   Skip going through character bases/growths
            if 'characters' in file:
                continue
            data=read_stat_table(game,file)
            #   Will get right class name per section
            proper_class=match_class_name(game,unit,unit_class,file)
            #   For names that do not appear in some lists, like promoted classes
            if proper_class not in data.index:
                continue
            if 'growth-rates' in file:
                key='class-growths'
            elif 'maximum-stats' in file:
                key='maxes'
            elif 'promotion-gains' in file:
                key='promo'
            class_stats=data.loc[proper_class,:]
            attr[key]=class_stats
    if 'promo' in attr.keys():
        x=attr['promo']
        if len(x) > 1:
            t=promo_dict(game)
            if unit in t.keys():
                promo_path=t[unit]
            assert 0 <= promo_path < len(x)
            attr['promo']=x.iloc[promo_path,:]
    return attr


def load_unit_table(game,unit,lyn_mode=False):
    args=game,unit,lyn_mode
    columns={}
    class_attr=load_class_attributes(*args)
    unit_attr=load_unit_attributes(*args)
    columns.update(unit_attr)
    columns.update(class_attr)
    unit_data=pd.concat(columns,axis=1)
    if game == '5':
        maxes_data='.','metadata','fe5_maxes.csv'
        maxes_data=os.path.sep.join(maxes_data)
        fe5_maxes=pd.read_csv(maxes_data,index_col=0,header=None)
        unit_data.insert(loc=0,column='maxes',value=fe5_maxes)
    unit_data=unit_data.fillna(value=0)
    return unit_data


def test_character_attr(game=4):
    game=str(game)
    lords={
        '4':'Sigurd',
        '5':'Leaf',
        '6':'Roy',
        '7':'Eliwood',
        '8':'Eirika',
        '9':'Ike'
        }
    unit=lords[game]
    args=game,unit
    x=load_unit_attributes(*args)
    y=load_class_attributes(*args)
    z=load_unit_info(*args)
    print('unit')
    for xx in x.values():
        print(xx)
    print('class')
    for yy in y.values():
        print(yy)
    print('info')
    for zz in z.items():
        print(zz)


if __name__=='__main__':
    k=5
    game=str(k)
    lord={
        '4':'Sigurd',
        '5':'Leaf',
        '6':'Roy',
        '7':'Eliwood',
        '8':'Eirika',
        '9':'Ike'
        }
    unit=lord[game]
    unit='Lara'
    x=load_unit_table(game,unit)
    print(x)
