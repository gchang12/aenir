from aenir2.read_stats import *
from aenir2.quintessence import Morph

def test_stat_retrieval(game='5',unit=''):
    lord={
        '4':'Sigurd',
        '5':'Leaf',
        '6':'Roy',
        '7':'Eliwood',
        '8':'Eirika',
        '9':'Ike'
        }
    if not unit:
        unit=lord[game]
    args=game,unit,lyn_mode
    test_cases=load_character_bases,\
                load_character_growths,\
                load_class_maxes,\
                load_class_promo,\
                load_class_growths
    all_data=()
    unit_info=load_unit_info(*args)
    indices=()
    for case in test_cases:
        data=case(*args)
        if data is None:
            continue
        all_data+=(data,)
        index_copy=tuple(data.index)
        if index_copy not in indices:
            indices+=(index_copy,)
    df=pd.DataFrame(all_data)
    for item in unit_info.items():
        print(item)
    print(df)
    same_indices=len(indices) == 1
    message='All columns have identical indices: %s'%same_indices
    print(message)


def test_class_promo_dict(game='8',promo_path=1):
    x=load_class_promo_dict(game,promo_path=promo_path)
    for stuff in x.items():
        print(stuff)


def test_unit_list(game='7',lyn_mode=False):
    file_match='characters_base-stats'
    if lyn_mode:
        y='1'
    else:
        y='2'
    file_match+=y
    x=character_list(game,file_match=file_match)
    for unit in x:
        print(unit)

def test_child_list():
    x=fe4_child_list()
    for m in x:
        print(m)


def test_child_hunt(unit='Rana',father='Claude'):
    args='4',unit
    test_cases=load_character_bases,\
                load_character_growths
    all_data=()
    unit_info=load_unit_info(*args,father=father)
    indices=()
    for case in test_cases:
        data=case(*args,father=father)
        if data is None:
            continue
        all_data+=(data,)
        index_copy=tuple(data.index)
        if index_copy not in indices:
            indices+=(index_copy,)
    df=pd.DataFrame(all_data)
    for item in unit_info.items():
        print(item)
    print(df)
    same_indices=len(indices) == 1
    message='All columns have identical indices: %s'%same_indices
    print(message)


def test_match_name(unit='Ross',\
                    class_name='Journeyman (2)',\
                    match_against_maxes=True):
    game='8'
    if match_against_maxes:
        filename='classes_maximum-stats.csv'
    else:
        filename='classes_promotion-gains.csv'
    x=match_class_name(game,unit,'Journeyman (2)',filename,audit='promo')
    print(x)


def test_wallace(lyn_mode=True):
    kwargs={
        'game':'7',\
        'unit':'Wallace',\
        'lyn_mode':lyn_mode
        }
    unit_info=load_unit_info(**kwargs)
    unit_promotions=load_class_promo_list(**kwargs)
    print(unit_info)
    print(unit_promotions)

    
if __name__ == '__main__':
    k=7
    game=str(k)
    unit='Wallace'
    kwargs={}
    kwargs['game']=game
    kwargs['unit']=unit
    #test_child_hunt()
    test_wallace(lyn_mode=True)
    #test_stat_retrieval(**kwargs)
    #x=load_class_promo_list(**kwargs)
    #print(x)
    #x=load_class_promo_list(game,unit)
    #print(x)
