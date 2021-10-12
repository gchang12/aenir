from bs4 import BeautifulSoup
from requests import get

from os import mkdir
from os.path import sep, exists

import pandas as pd
import json
import re

from aenir2.data_fetcher import get_nickname

class RankFetcher:
    def __init__(self,game):
        self.root='https://serenesforest.net'
        self.game=game
        self.title=get_nickname(game)
        self.main_dir=sep.join(['.','class_data'])
        self.game_dir=sep.join([self.main_dir,'fe%s'%game])
        self.ranks=dict()

    def outputFile(self,filename):
        return sep.join([self.game_dir,filename])

    def createDir(self):
        folders=self.main_dir,self.game_dir
        for f in folders:
            if not exists(f):
                mkdir(f)

    def joinUrl(self,section=None):
        url=[self.root,self.title]
        if section is None:
            url.append('')
        else:
            portals='classes',section
            for portal in portals:
                url.append(portal)
        return '/'.join(url)

    def rankDict(self):
        d=dict()
        file=sep.join([self.main_dir,r'weapon-types.txt'])
        with open(file) as rfile:
            for n,line in enumerate(rfile.readlines(),start=1):
                line=line.strip()
                line=line.split(',')
                if self.game == '4':
                    d[n]=line[0]
                else:
                    d[line[1]]=line[0]
        return d

    def saveRanks(self):
        dst=self.outputFile('weapon-ranks.json')
        self.cleanupRanks()
        with open(dst,'w') as wfile:
            json.dump(self.ranks,wfile)

    def ranksFromFile(self):
        dst=self.outputFile('weapon-ranks.json')
        with open(dst,'r') as rfile:
            self.ranks=json.load(rfile)

    def cleanupRanks(self):
        new_ranks=dict()
        for key,val in self.ranks.items():
            if not val:
                continue
            new_ranks[key]=val
        self.ranks=new_ranks

    def getSoup(self,section):
        url=self.joinUrl(section=section)
        soup=BeautifulSoup(get(url).text,'html.parser')
        return soup

    def getRanks4(self):
        assert self.game == '4'
        soup=self.getSoup('weapon-ranks')
        alphabet='A','B','C'
        indices=self.rankDict()
        for tr in soup.find_all('tr'):
            ranks=list()
            for n,td in enumerate(tr.find_all('td')):
                if n == 0:
                    unit_class=td.text
                    if '*' in unit_class:
                        continue
                    unit_class=unit_class.strip()
                    self.ranks[unit_class]=ranks
                else:
                    letter=td.text
                    letter=letter.strip()
                    if letter in alphabet:
                        weapon_type=indices[n]
                        ranks.append(weapon_type)
        self.saveRanks()

    def getRanks9(self):
        assert self.game == '9'
        weapon_dict=self.rankDict()
        soup=self.getSoup('base-stats')
        knifers='Sage','Thief','Assassin'
        for tr in soup.find_all('tr'):
            ranks=list()
            for n,td in enumerate(tr.find_all('td')):
                if n == 0:
                    unit_class=td.text
                    if '*' in unit_class:
                        continue
                    unit_class=unit_class.strip()
                    self.ranks[unit_class]=ranks
                    for hoodlum in knifers:
                        if hoodlum in unit_class:
                            ranks.append('knives')
                elif td.text.isnumeric():
                    continue
                else:
                    description=td.text
                    for weapon in weapon_dict.keys():
                        if weapon in description:
                            weapon=weapon_dict[weapon]
                            ranks.append(weapon)
        self.saveRanks()

    def getImgRanks(self):
        if self.game == '4':
            return self.getRanks4()
        elif self.game == '9':
            return self.getRanks9()
        soup=self.getSoup('base-stats')
        rank_dict=self.rankDict()
        for tr in soup.find_all('tr'):
            ranks=list()
            for n,td in enumerate(tr.find_all('td')):
                if n == 0:
                    unit_class=td.text
                    self.ranks[unit_class]=ranks
                elif td.find('a') is None:
                    continue
                else:
                    for a in td.find_all('a'):
                        for img in a.find_all('img'):
                            alt=img['alt']
                            if alt in rank_dict.keys():
                                alt=rank_dict[alt]
                                ranks.append(alt)
        self.saveRanks()

    def filterRanks5(self,text_list):
        assert self.game == '5'
        if ',' not in text_list:
            return [True]
        bool_list=list()
        text_list=text_list.split(',')
        for text in text_list:
            text=text.strip()
            greyed=re.match('[(]',text)
            if greyed is None:
                x=True
            else:
                x=False
            bool_list.append(x)
        return bool_list

    def getMoreRanks5(self):
        assert self.game == '5'
        soup=self.getSoup('base-stats')
        self.getImgRanks()
        text_dict=dict()
        rank_dict=self.ranks
        for tr in soup.find_all('tr'):
            ranks=list()
            for n,td in enumerate(tr.find_all('td')):
                if n == 0:
                    unit_class=td.text
                    text_dict[unit_class]=ranks
                elif td.find('a') is None:
                    continue
                else:
                    bool_list=self.filterRanks5(td.text)
                    ranks.extend(bool_list)
        for key in text_dict.keys():
            if key not in rank_dict.keys():
                continue
            old_list=rank_dict[key]
            bool_list=text_dict[key]
            assert len(old_list) == len(bool_list)
            new_list=list()
            for weapon,tf in zip(old_list,bool_list):
                if tf:
                    new_list.append(weapon)
            self.ranks[key]=new_list

        self.saveRanks()

def correct_fe5():
    game='5'
    x=RankFetcher(game)
    x.getMoreRanks5()

def save_all():
    for n in range(4,10):
        game=str(n)
        x=RankFetcher(game)
        x.createDir()
        x.getImgRanks()

if __name__ == '__main__':
    correct_fe5()
