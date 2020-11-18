from aenir2.quintessence import Morph

def test_trainee(unit='Ross'):
    trainees='Ross','Amelia','Ewan','Lara'
    assert unit in trainees
    kwargs={}
    game='8'
    if unit == 'Lara':
        game='5'
    kwargs['game']=game
    kwargs['unit']=unit
    x=Morph(**kwargs)
    actions=x.level_up,x.promote,x.promote,x.promote
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


def test_hugh(num_times=3):
    args='6','Hugh'
    x=Morph(*args)
    print(x.my_stats)
    x.decline_hugh(num_times)
    print(x.my_stats)


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
    print(a,b,c,d)


if __name__ == '__main__':
    test_forecast()
