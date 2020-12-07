from aenir2.gender_dict import gender_dict,promo_dict
from aenir2.stat_table import *
from aenir2.name_lists import *

def match_class_name(game,unit,class_name,filename,audit):
    assert 'classes' in filename
    categories={
        'base-stats':'bases',\
        'growth-rates':'growths',\
        'maximum-stats':'maxes',\
        'promotion-gains':'promo'
        }

    for substring,codename in categories.items():
        if substring in filename:
            code=categories[substring]
            break

    gender_for=gender_dict(game)
    suffix=gender_for[unit]
    x=read_stat_table(game,filename)
    match_list=x.index
    name_matches=read_class_names2(game,audit,code)

    gendered_class=class_name+suffix

    #   Check if name without suffix appears in page
    if class_name in match_list:
        return class_name

    #   Check if gendered version of that name appears
    if gendered_class in match_list:
        return gendered_class

    #   Check if name with gender-suffix appears
    if class_name in name_matches.keys():
        proper_name=name_matches[class_name]
        if proper_name in match_list:
            return proper_name
        gendered_class2=proper_name+suffix
        if gendered_class2 in match_list:
            return gendered_class2

    #   Check if corrected version of name appears
    if gendered_class in name_matches.keys():
        proper_name=name_matches[gendered_class]
        if proper_name in match_list:
            return proper_name
        elif ' (' in proper_name:
            parenthesis_loc=proper_name.index(' (')
            ungen_class=proper_name[:parenthesis_loc]
            if ungen_class in match_list:
                return ungen_class


def get_class_name(game,unit,class_name,audit):
    proper_name=lambda filename: match_class_name(game,unit,class_name,filename,audit)
    return proper_name

if __name__ == '__main__':
    filenames={
        'promo':'classes_promotion-gains.csv',\
        'maxes':'classes_maximum-stats.csv',
        }
    game='8'
    unit='Ross'
    class_name='Journeyman (2)'
    game='6'
    unit='Gonzales'
    class_name='Bandit'
    unit='Dayan'
    class_name='Nomadic Trooper'
