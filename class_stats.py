import json
import pandas as pd

from os.path import sep

from aenir2.class_matcher import ClassMatcher
from aenir2.growths_parser import GrowthsParser
from aenir2.rank_fetcher2 import RankFetcher2

class ClassStats:
    def __init__(self,game,unit_class):
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

    def getGrowths(self,uncommon=None):
        assert unit_class in self.name_list
        if self.game in ('4','5'):
            x=GrowthsParser(self.game)
            if self.game == '4':
                func=x.getGrowths4
            else:
                func=lambda y: x.getGrowths5(y,uncommon=uncommon)
        else:
            x=ClassMatcher(self.game)
            func=x.getGrowths
        return func(unit_class)

    def getBases(self):
        file=self.inputFile('classes_base-stats.csv')
        data=pd.read_csv(file,index_col=0)
        row=data.loc[unit_class,:]
        return row.to_numpy()

    def getRanks(self):
        rf2=RankFetcher2(self.game)
        ranks=rf2.ranksFromFile()[unit_class]
        return tuple(ranks)

    def getPromo(self):
        # Match bases to promo-names first
        x=4

    def getMaxes(self):
        # Match bases and promo to maxes-names first
        x=4

    def getSkills(self):
        # Get skills from FE5,8,9 first
        # - FE4 has character skills which are inherited and stuff
        x=5

    def getWeaknesses(self):
        # Manually write text file containing weaknesses
        x=44

if __name__ == '__main__':
    game='4'
    unit_class='Swordfighter'
    x=ClassGrowths(game)
    y=x.getBases(unit_class)
    print(y)
