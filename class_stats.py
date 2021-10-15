import json
import pandas as pd

from os.path import sep

from aenir2.name_matcher3 import ClassMatcher
from aenir2.growths_parser import GrowthsParser
from aenir2.rank_fetcher import RankFetcher

class ClassStats:
    def __init__(self,game,unit_class):
        self.game=game
        self.main_dir=sep.join(['.','class_data','fe%s'%game])
        self.unit_class=unit_class
        if game == '4':
            filename='classes_growth-rates.json'
        else:
            filename='name_dict.json'
        filename=self.inputFile(filename)
        with open(filename) as rfile:
            self.name_list=tuple(json.load(rfile).keys())

    def inputFile(self,filename):
        return sep.join([self.main_dir,filename])

    def growthsName(self):
        if self.game == '4':
            return self.unit_class
        file=self.inputFile('name_dict.json')
        with open(file) as rfile:
            d=json.load(rfile)
        return d[self.unit_class]

    def getGrowths(self,uncommon=None):
        unit_class=self.growthsName()
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
        row=data.loc[self.unit_class,:]
        return row.to_numpy()

    def getRanks(self):
        rf2=RankFetcher(self.game)
        ranks=rf2.ranksFromFile()[self.unit_class]
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
    n=9
    game=str(n)
    class_dict={
        '4':'Swordfighter',\
        '5':'Sword Fighter (F)',\
        '6':'Myrmidon (F)',\
        '7':'Myrmidon (F)',\
        '8':'Myrmidon (F)',\
        '9':'Myrmidon (F)'
        }
    unit_class=class_dict[game]
    x=ClassStats(game,unit_class)
    stats={
        'bases':x.getBases(),\
        'growths':x.getGrowths(),\
        'ranks':x.getRanks()
        }
    print(stats)
