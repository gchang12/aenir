import json

from os.path import sep

from aenir2.class_matcher import ClassMatcher
from aenir2.growths_parser import GrowthsParser

class ClassGrowths:
    def __init__(self,game):
        self.game=game
        self.main_dir=sep.join(['.','class_data','fe%s'%game])
        if game == '4':
            filename='classes_growth-rates.json'
        else:
            filename='name_dict.json'
        filename=self.inputFile(filename)
        with open(filename) as rfile:
            self.name_list=tuple(json.load(rfile).keys())

    def inputFile(self,filename):
        return sep.join([self.main_dir,filename])

    def getGrowths(self,unit_class):
        if self.game in ('4','5'):
            x=GrowthsParser(self.game)
            if self.game == '4':
                func=x.getGrowths4
            else:
                func=x.getGrowths5
        else:
            x=ClassMatcher(self.game)
            func=x.getGrowths
        return func(unit_class)

if __name__ == '__main__':
    game='4'
    unit_class='Swordfighter'
    x=ClassGrowths(game)
    y=x.getGrowths(unit_class)
    print(y)
