import json
import pandas as pd
import re

from os import walk, mkdir
from os.path import sep, exists

class DataDict2:
    def __init__(self,game):
        self.game=game
        self.stat_dir=sep.join(['.','raw_data','fe%s'%game])
        self.promo_file=sep.join([self.stat_dir,'classes_promotion-gains.csv'])
        self.class_dir=sep.join(['.','class_data'])
        game_class_dir=sep.join([self.class_dir,'fe%s'%game])
        self.item_file=sep.join([game_class_dir,'weapon-ranks.json'])
        self.audit_dir=sep.join(['.','audit'])
        self.game_dir=sep.join([self.audit_dir,'fe%s'%game])
        directories=self.class_dir,game_class_dir,self.audit_dir,self.game_dir
        for folder in directories:
            if not exists(folder):
                mkdir(folder)
        with open(self.item_file,'r') as rfile:
            self.main_names=tuple(json.load(rfile))
        self.filenames='in-ranks_not-stats','in-stats_not-ranks'
        self.filename_dict={
            'promo':'ranks-and-promo',\
            'bases':'ranks-and-bases'
            }

    def gatherBasesNames(self):
        pattern='characters_base-stats'
        names=list()
        for x,y,filelist in walk(self.stat_dir):
            for file in filelist:
                if not re.match(pattern,file):
                    continue
                file=sep.join([self.stat_dir,file])
                data=pd.read_csv(file,index_col=0)
                bases_names=list(data.loc[:,'Class'])
                names.extend(bases_names)
        return set(names)

    def gatherPromoNames(self):
        data=pd.read_csv(self.promo_file,index_col=0)
        if self.game == '7':
            names=list(data.index)
        else:
            names=list(data.loc[:,'Promotion'])
        return set(names)

    def getIntersection(self,keyword):
        assert keyword in self.filename_dict.keys()
        if keyword == 'promo':
            iterable=self.gatherPromoNames()
        else:
            iterable=self.gatherBasesNames()
        iterable=set(iterable)
        main_names=set(self.main_names)
        intersection=set.intersection(iterable,main_names)
        return list(intersection)

    def auditNames(self):
        diff=list()
        for name in self.main_names:
            if name in self.gatherPromoNames():
                continue
            elif name in self.gatherBasesNames():
                continue
            else:
                diff.append(name)
        return diff

    def inverseAuditG(self,section):
        assert section in ('promo','bases')
        diff=list()
        genders=' (M)',' (F)'
        if section == 'bases':
            iterable=self.gatherBasesNames()
        else:
            iterable=self.gatherPromoNames()
        for name in iterable:
            if name.isnumeric():
                continue
            if name not in self.main_names:
                contains_gname=False
                for g in genders:
                    g_name=name+g
                    if g_name in self.main_names:
                        contains_gname=True
                        break
                if not contains_gname:
                    diff.append(name)
        return diff

    def inverseAudit(self,section):
        assert section in ('promo','bases')
        diff=list()
        if section == 'bases':
            iterable=self.gatherBasesNames()
        else:
            iterable=self.gatherPromoNames()
        for name in iterable:
            if name.isnumeric():
                continue
            if name not in self.main_names:
                diff.append(name)
        return diff

    def invAuditNames(self,gendered=False):
        if gendered:
            func=self.inverseAuditG
        else:
            func=self.inverseAudit
        diff=list()
        sections=('promo','bases')
        for section in sections:
            diff.extend(func(section))
        diff=set(diff)
        diff=list(diff)
        return diff

    def saveInvAuditsG(self):
        sections=('promo','bases')
        iterable=self.invAuditNames(gendered=True)
        filename='in-stats_not-ranks_G'
        self.saveAsJSON(iterable,filename)
        self.writeText(filename,iterable)

    def outputFile(self,filename):
        return sep.join([self.game_dir,filename])

    def saveAsJSON(self,iterable,filename):
        if '.' not in filename:
            filename=filename+'.json'
        else:
            N=filename.index('.')
            if filename[N:] != '.json':
                filename=filename[:N]+'.json'
        filename=self.outputFile(filename)
        if not iterable:
            iterable=None
        with open(filename,'w') as wfile:
            json.dump(iterable,wfile)

    def saveIntersections(self):
        keywords='bases','promo'
        for kw in keywords:
            iterable=self.getIntersection(kw)
            filename=self.filename_dict[kw]
            self.saveAsJSON(iterable,filename)
            self.writeText(filename,iterable)

    def saveAll(self):
        for n,name in enumerate(self.filenames):
            if n == 0:
                iterable=self.auditNames()
            else:
                iterable=self.invAuditNames()
            self.saveAsJSON(iterable,name)

    def writeText(self,list_name,iterable):
        list_name=self.outputFile(list_name+'.txt')
        with open(list_name,'w') as wfile:
            for x in iterable:
                wfile.write(x+'\n')

    def convertToText(self):
        for name in self.filenames:
            json_file=name+'.json'
            json_file=self.outputFile(json_file)
            with open(json_file,'r') as rfile:
                json_list=json.load(rfile)
            self.writeText(name,json_list)

    def __call__(self):
        self.saveAll()
        self.convertToText()


def compile_data(n):
    game=str(n)
    x=DataDict2(game)
    x()

def compile_gdata(n):
    game=str(n)
    x=DataDict2(game)
    x.saveInvAuditsG()

def compile_all(func):
    for n in range(4,10):
        func(n)

def compile_intersection(n):
    game=str(n)
    x=DataDict2(game)
    x.saveIntersections()

if __name__ == '__main__':
    n=4
    compile_gdata(n)
    #compile_all(compile_gdata)
