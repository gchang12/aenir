from aenir2.quintessence import Morph
from aenir2.name_lists import character_list

def test_trainee(unit='Ross',test_auto_level=False):
    trainees='Ross','Amelia','Ewan','Lara'
    assert unit in trainees
    kwargs={}
    game='8'
    if unit == 'Lara':
        game='5'
    kwargs['game']=game
    kwargs['unit']=unit
    x=Morph(**kwargs)
    if test_auto_level:
        #   base class -> promote -> promote -> promote (for Lara)
        actions=x.promote,x.promote,x.promote
    else:
        #   Promote at max-level every time
        actions=[x.level_up,x.promote]
        actions+=actions
        if unit == 'Lara':
            actions+=actions
    attribute_names='levels','classes','stats','maxes','promo'
    message= lambda y,z: ('%8s'%y,z)
    print(x.unit_info)
    for action in actions:
        if action == x.level_up:
            action(20)
        else:
            action()
        attributes=x.my_levels,x.my_classes,x.my_stats,x.my_maxes,x.my_promotions
        for attribute,name in zip(attributes,attribute_names):
            l=message(name,attribute)
            print(l)
            #print(name,attribute)
    if unit == 'Ross':
        url='https://serenesforest.net/the-sacred-stones/characters/average-stats/ross/fighter/warrior/'
        print(url)


def test_hugh(num_times=3):
    args='6','Hugh'
    x=Morph(*args)
    print(x.my_stats)
    print(x.my_levels)
    x.decline_hugh(num_times)
    print(x.my_stats)
    x.level_up(5)
    x.promote()
    print(x.my_stats)
    hugh_avg='https://serenesforest.net/binding-blade/characters/average-stats/normal-mode/hugh-5000g/'
    print(hugh_avg)


def test_stat_booster(stat_name='HP'):
    args='6','Thany'
    x=Morph(*args)
    print(x.my_stats)
    x.use_stat_booster(stat_name)
    print(x.my_stats)


def test_hard_mode(chapter='16'):
    assert chapter in ('12','16','20','22')
    args='6','Cath'
    x=Morph(*args)
    print(x.my_stats,x.my_levels)
    x.add_hm_bonus(chapter=chapter)
    print(x.my_stats,x.my_levels)


def test_auto_level(chapter='13'):
    assert chapter in ('9','13')
    args='8','Amelia'
    x=Morph(*args)
    print(x.base_stats,x.my_levels.copy())
    x.add_auto_bonus(chapter)
    print(x.my_stats,x.my_levels)
    print(x.my_stats-x.base_stats)


def test_gonzales(chapter='10B'):
    assert chapter in ('10B','10A')
    args='6','Gonzales'
    x=Morph(*args)
    print(x.my_stats,x.my_levels)
    x.add_auto_bonus(chapter)
    print(x.my_stats,x.my_levels)
    print(x.my_stats == x.base_stats)


def test_fe8_lord():
    args='8','Eirika'
    x=Morph(*args)
    base_lv=x.my_levels[0]
    print(*args)
    print(x.my_stats,x.my_levels.copy())
    x.add_auto_bonus()
    print(x.my_stats,x.my_levels)
    bonus=x.my_stats-x.base_stats
    bonus/=(15-base_lv)
    print(bonus)
    args='8','Ephraim'
    print(*args)
    x=Morph(*args)
    base_lv=x.my_levels[0]
    print(x.my_stats,x.my_levels.copy())
    x.add_auto_bonus()
    print(x.my_stats,x.my_levels)
    new_bonus=x.my_stats-x.base_stats
    new_bonus/=(15-base_lv)
    print(new_bonus is bonus)


def test_forecast():
    args='6','Gonzales'
    y=Morph(*args)
    #   Need to promote
    y.add_auto_bonus('10B')
    a=y.add_hm_bonus(get_forecast=True)
    b=y.level_up(20,get_forecast=True)
    c=y.promote(get_forecast=True)
    d=y.use_stat_booster('HP',get_forecast=True)
    y.promote()
    print(y.my_maxes)
    print(a,b,c,d)


def test_fe7_lord(max_out=False,unit='Eliwood'):
    fe7_lords='Eliwood','Hector','Lyn'
    assert unit in fe7_lords
    args='7',unit
    x=Morph(*args)
    print(x.my_levels)
    print(x.my_stats)
    if max_out:
        x.level_up(19)
    x.promote()
    print(x.my_stats)
    url='https://serenesforest.net/blazing-sword/characters/average-stats/eliwood/'
    print(url)


def test_fe7_dancer(unit='Ninian',in_list=False):
    assert unit in ('Ninian','Nils')
    if in_list:
        fe7_unit_list=character_list('7')
        y=unit in fe7_unit_list
        for person in fe7_unit_list:
            print(person)
        print('\nNils in unit list: %s'%y)
        return
    args='7',unit
    x=Morph(*args)
    print(x.base_stats)
    x.level_up(20)
    print(x.my_stats)
    print(x.maximum_stats)
    url='https://serenesforest.net/blazing-sword/characters/average-stats/nils/'
    print(url)


if __name__ == '__main__':
    test_fe7_dancer('Nils')
    #test_fe7_lord(True)
    #test_trainee()
