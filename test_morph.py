from aenir2.quintessence import Morph

def test_morph_trainee(unit='Ross'):
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


if __name__ == '__main__':
    test_morph_trainee(unit='Lara')
