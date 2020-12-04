from aenir2.name_lists import character_list,\
     translated_character_list,\
     get_stat_names,\
     fe4_child_list,\
     game_title_dict
from aenir2.gender_dict import max_level_dict,\
     updated_name_for,\
     hard_mode_dict,\
     auto_level_dict,\
     booster_dict,\
     chapter_dict

#   Conditions that Limstella class needs to check before initialization

def max_level(game,class_name):
    args=(game,class_name)
    max_level=max_level_dict(*args)
    return max_level

def is_lyndis_league(game,unit):
    #   Essential to summoning Lyn Mode dialog box
    if game != '7':
        return False
    kwargs={
        'game':game,\
        'file_match':'characters_base-stats1.csv'
        }
    unit_list=character_list
    lyndis_league=unit_list(**kwargs)
    return unit in lyndis_league

def is_fe4_child(game,unit):
    #   Essential to summoning father selection window
    if game != '4':
        return False
    else:
        return unit in fe4_child_list()

#   Getting lists

def fe4_father_list():
    father_list=fe4_child_list(get_father=True)
    kwargs={
        'game':'4',\
        'raw_list':father_list
        }
    return translated_character_list(**kwargs)

def unit_list(game):
    file_match='characters_growth-rates'
    kw={
        'game':game,\
        'file_match':file_match
        }
    from_growths=translated_character_list(**kw)
    file_match='characters_base-stats'
    if game == '7':
        file_match+='2'
    kw['file_match']=file_match
    from_bases=translated_character_list(**kw)
    list_of_units=()

    for name in from_bases:
        if name in from_growths:
            list_of_units+=(name,)

    return list_of_units

#   For displayed unit names

def get_old_name(game,unit):
    return updated_name_for(game,unit,new_to_old=True)

#   After initialization of Morph object

def is_hugh(game,unit):
    #   Use self.decline_hugh method
    return (game,unit) == ('6','Hugh')

def has_hm_bonus(game,unit):
    return unit in hard_mode_dict().keys()

def has_auto_bonus(game,unit):
    return unit in auto_level_dict().keys()

def get_hm_chapters(unit):
    d=hard_mode_dict()[unit]
    if '' not in d.keys():
        return tuple(d.keys())
    else:
        return ()

def get_auto_chapters(unit):
    d=auto_level_dict()[unit]
    return tuple(d.keys())

def booster_to_stat_converter(game,booster_name):
    d=booster_dict(game,get_bonus=False)
    t={}
    for stat_name,item in d.items():
        t[item]=stat_name
    return t

#   Checks if certain actions permissible (e.g. level-up, promote)

def can_auto_level_fe8_lord(game,unit,current_level):
    if game != '8':
        return False
    elif unit not in ('Ephraim','Eirika'):
        return False
    return current_level >= 15

def decline_hugh_dict():
    d={
        '10,000':0,\
        '8,000':1,\
        '6,000':2,\
        '5,000':3
        }
    return d

def chapter_name_dict(game,unit,chapter_function):
    chapter_list=chapter_function(unit)
    chapter_names={}
    for title,chapter in chapter_dict(game).items():
        if chapter in chapter_list:
            chapter_names[title]=chapter
    return chapter_names

def auto_chapter_dict(game,unit):
    chapter_function=get_auto_chapters
    args=game,unit,chapter_function
    return chapter_name_dict(*args)

def hm_chapter_dict(game,unit):
    chapter_function=get_hm_chapters
    args=game,unit,chapter_function
    return chapter_name_dict(*args)

dummy_message='\n\nEnter: Confirm selection.'

if __name__ == '__main__':
    x=unit_list('5')
    for l in x:
        print(l)
