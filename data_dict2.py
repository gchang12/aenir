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
        self.json_dir=sep.join(['.','json'])
        self.json_output_dir=sep.join([self.json_dir,'fe%s'%self.game])
        my_directories=(self.junk_dir,self.output_dir,self.json_dir,self.json_output_dir)
        for folder in my_directories:
            if not exists(folder):
                mkdir(folder)
        with open(self.item_file,'r') as rfile:
            self.main_names=tuple(json.load(rfile))
        self.non_matches=dict()
        self.checklist={
            'bases':'characters_base-stats',\
            'promo':'classes_promotion-gains'
            }

    def matchNames(self,checklist,file):
        matched=list()
        for check in checklist:
            x=re.match(check,file)
            x=bool(x)
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
            if self.game != '7':
                promo_list=data.loc[:,'Promotion'].to_list()
                stat_classes.extend(promo_list)
        for name in self.main_names:
            if name not in stat_classes:
                non_matches.append(name)
        self.non_matches[file]=non_matches

    def saveNonMatches(self):
        for key,values in self.non_matches.items():
            key=key[:-4]+'.txt'
            filename=sep.join([self.output_dir,key])
            with open(filename,'w') as wfile:
                for val in values:
                    wfile.write(val+'\n')

    def listFromFile(self,file):
        file=sep.join([self.output_dir,file])
        my_list=list()
        with open(file,'r') as rfile:
            for line in rfile.readlines():
                line=line.strip()
                my_list.append(line)
        return my_list

    def mergeBaseNonMatches(self):
        pattern=self.checklist['bases']
        match_list=list()
        for x,y,filelist in walk(self.output_dir):
            if len(filelist) <= 2:
                return
            num_dups=len(filelist)-1
            for file in filelist:
                if re.match(pattern,file):
                    base_matches=self.listFromFile(file)
                    match_list.extend(base_matches)
        new_list=list()
        for element in match_list:
            count=match_list.count(element)
            if count == num_dups:
                new_list.append(element)
        return new_list

    def saveToJSON(self,filename,iterable):
        if '.txt' in filename:
            filename=filename.replace('.txt','.json')
        filename=sep.join([self.json_output_dir,filename])
        with open(filename,'w') as wfile:
            json.dump(iterable,wfile)

    def firstMerge(self):
        base=self.checklist['bases']+'.txt'
        if self.mergeBaseNonMatches is None:
            base_list=self.listFromFile(base)
        else:
            base_list=self.mergeBaseNonMatches()
        promo=self.checklist['promo']+'.txt'
        promo_list=self.listFromFile(promo)
        base='bases.json'
        promo='promo.json'
        self.saveToJSON(base,base_list)
        self.saveToJSON(promo,promo_list)

    def listFromJSON(self,name):
        if '.json' not in name:
            name=name+'.json'
        name=sep.join([self.json_output_dir,name])
        with open(name,'r') as rfile:
            name=json.load(rfile)
        if name is None:
            return set()
        else:
            return set(name)

    def secondMerge(self):
        base=self.listFromJSON('bases')
        promo=self.listFromJSON('promo')
        base_and_promo=set.intersection(base,promo)
        only_promo=promo-base_and_promo
        only_base=base-base_and_promo
        filelist='base-and-promo','bases-only','promo-only'
        setlist=base_and_promo,only_base,only_promo
        for file,s in zip(filelist,setlist):
            file=file+'.json'
            if not s:
                s=None
            else:
                s=tuple(s)
            self.saveToJSON(file,s)

    def checkClassNames(self):
        checklist=(
            'characters_base-stats',\
            'classes_promotion-gains'
            )
        for x,y,filelist in walk(self.stat_dir):
            if not filelist:
                continue
            for file in filelist:
                is_correct_file=self.matchNames(checklist,file)
                if not is_correct_file:
                    continue
                self.compareNames(file)
        self.saveNonMatches()

if __name__ == '__main__':
    for n in range(4,10):
        game=str(n)
        x=DataDict2(game)
        x.secondMerge()
