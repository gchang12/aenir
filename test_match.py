from aenir2.match_names import *

def test_match(**kwargs):
    x=match_class_name(**kwargs)
    print(x)
    
def test_get_class_name(game,unit,class_name):
    y=get_class_name(game,unit,class_name,lyn_mode=False)
    print(y)

def test_unit(game,unit,class_name,filename,audit):
    test_match(game,unit,class_name,filename,audit=audit)
    test_get_class_name(game,unit,class_name)

def test_unit(filename='classes_promotion-gains.csv',audit='bases'):
    game='8'
    unit='Ephraim'
    class_name='Lord'
    test_unit(game,unit,class_name,filename,audit)

def test_ross(filename='classes_promotion-gains.csv',audit='bases'):
    game='8'
    unit='Ross'
    class_name='Journeyman (2)'
    test_unit(game,unit,class_name,filename,audit)

def test_gonzales(filename='classes_promotion-gains.csv',audit='bases'):
    game='6'
    unit='Gonzales'
    class_name='Bandit'
    test_unit(game,unit,class_name,filename,audit)

def test_dayan(filename='classes_promotion-gains.csv',audit='bases'):
    game='6'
    unit='Dayan'
    class_name='Nomadic Trooper'
    test_unit(game,unit,class_name,filename,audit)


if __name__ == '__main__':
    filename='classes_maximum-stats.csv'
    audit='promo'
    kwargs={}
    kwargs={'filename':filename,'audit':audit}
