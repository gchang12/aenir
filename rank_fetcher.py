from bs4 import BeautifulSoup
from requests import get

from os import mkdir
from os.path import sep, exists

import pandas as pd
import json

from aenir2.data_fetcher import get_nickname

class RankFetcher:
    def __init__(self,game):
        self.root='https://serenesforest.net'
        self.game=game
        self.title=get_nickname(game)
        self.main_dir=sep.join(['.','weapon_ranks'])
        self.ranks=dict()

    def createDir(self):
        if not exists(self.main_dir):
            mkdir(self.main_dir)

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
        dst=sep.join([self.main_dir,'fe%s.json'%self.game])
        self.cleanupRanks()
        with open(dst,'w') as wfile:
            json.dump(self.ranks,wfile)

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

if __name__ == '__main__':
    n=9
    game=str(n)
    x=RankFetcher(game)
    x.getImgRanks()
