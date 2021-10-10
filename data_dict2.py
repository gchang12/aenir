import json
import pandas as pd
import re

from os import walk, mkdir
from os.path import sep, exists

class DataDict2:
    def __init__(self,game):
        self.game=game
        self.stat_dir=sep.join(['.','raw_data','fe%s'%self.game])
        self.item_file=sep.join(['.','weapon_ranks','fe%s.json'%self.game])
        self.junk_dir=sep.join(['.','junk_dir'])
        self.output_dir=sep.join([self.junk_dir,'fe%s'%self.game])
        for folder in (self.junk_dir,self.output_dir):
            if not exists(folder):
                mkdir(folder)
        with open(self.item_file,'r') as rfile:
            self.main_names=tuple(json.load(rfile))
        self.non_matches=dict()

    def matchNames(self,checklist,file):
        matched=list()
        for check in checklist:
            if re.match(check,file):
                x=True
            else:
                x=False
            matched.append(x)
        return any(matched)

    def compareNames(self,file):
        newfile=sep.join([self.stat_dir,file])
        data=pd.read_csv(newfile,index_col=0)
        non_matches=list()
        if 'characters' in file:
            stat_classes=data.loc[:,'Class'].to_list()
        else:
            stat_classes=list(data.index)
        for name in self.main_names:
            if name not in stat_classes:
                non_matches.append(name)
        self.non_matches[file]=non_matches

    def saveNonMatches(self):
        for key,values in self.non_matches.items():
            filename=sep.join([self.output_dir,key])
            with open(filename,'w') as wfile:
                for val in values:
                    wfile.write(val+'\n')

    def checkClassNames(self):
        checklist=(
            'characters_base-stats',\
            'classes_maximum-stats',\
            'classes_promotion-gains'
            )
        for x,y,filelist in walk(self.stat_dir):
            if not filelist:
                continue
            for file in filelist:
                if not self.matchNames(checklist,file):
                    continue
                self.compareNames(file)
        self.saveNonMatches()

if __name__ == '__main__':
    for n in range(5,10):
        game=str(n)
        x=DataDict2(game)
        x.checkClassNames()
