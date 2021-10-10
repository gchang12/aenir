from bs4 import BeautifulSoup
from requests import get

from os import mkdir
from os.path import sep, exists

import pandas as pd

from aenir2.data_fetcher import get_nickname

class Angelo:
    def __init__(self,game,dirname='weapon_data'):
        self.root='https://serenesforest.net'
        self.game=game
        self.title=get_nickname(game)
        self.main_dir=sep.join(['.',dirname])
        pathPointer=lambda x: sep.join([self.main_dir,x])
        self.game_dir=pathPointer('fe'+game)
        self.data_file=pathPointer('data-locations.txt')

    def createDir(self):
        dirs=self.main_dir,self.game_dir
        for d in dirs:
            if not exists(d):
                mkdir(d)

    def joinUrl(self,section=None,supsection='inventory'):
        url=[self.root,self.title]
        if section is None:
            url.append('')
        else:
            portals=supsection,section
            for portal in portals:
                url.append(portal)
        return '/'.join(url)

    def gatherUrl(self):
        game=self.title
        url=self.joinUrl()
        soup=BeautifulSoup(get(url).text,'html.parser')
        unneeded_pages=(
            'Items','Crusader Scrolls','Monster Weapons','Accessories'
            )
        url_contents=list()
        for a in soup.find_all('a'):
            if 'href' not in a.attrs:
                continue
            href=a['href']
            if 'inventory' not in href:
                if url_contents:
                    break
                else:
                    continue
            title=a.text
            if title in unneeded_pages:
                continue
            N=len(game)+len('inventory')+2
            href=href[N:]
            href=href.replace('/','')
            url_contents.append(href)
        return url_contents

    def recordUrl(self):
        url_contents=self.gatherUrl()
        with open(self.data_file,'a') as wfile:
            wfile.write(self.game+',')
            for portal in url_contents:
                wfile.write(portal+',')
            wfile.write('\n')

    def retrieveUrl(self):
        with open(self.data_file,'r') as rfile:
            for line in rfile.readlines():
                line=line.split(',')
                if line[0] != self.game:
                    continue
                return line[1:-1]

    def scrapeTable(self,table):
        data_list=list()
        for tr in table.find_all('tr'):
            headers=list()
            for th in tr.find_all('th'):
                header=th.text
                header=header.strip()
                if header not in headers:
                    headers.append(header)
                else:
                    break
            break
        data_list.append(headers)
        for tr in table.find_all('tr'):
            row=list()
            for td in tr.find_all('td'):
                cell=td.text
                if cell.isnumeric():
                    cell=int(cell)
                row.append(cell)
            if row:
                data_list.append(row)
        return data_list

    def scrapePage(self,section):
        url=self.joinUrl(section=section)
        if (self.game,section) in [('5','axes'),('6','anima-tomes')]:
            parser='html5lib'
        else:
            parser='html.parser'
        soup=BeautifulSoup(get(url).text,parser)
        page_contents=list()
        table_titles=list()
        kw={'index':None}
        for table in soup.find_all('table'):
            table=self.scrapeTable(table)
            header=table[0]
            kw['columns']=header
            kw['data']=table
            data=pd.DataFrame(**kw)
            page_contents.append(data.iloc[:,1:])
        if len(page_contents) > 1:
            for h3 in soup.find_all('h3'):
                title=h3.text
                if ' ' in title:
                    N=title.index(' ')
                    title=title[:N]
                title=title.lower()
                table_titles.append(title)
        if not table_titles:
            table_titles.append(None)
        page_dict=dict()
        for content,title in zip(page_contents,table_titles):
            page_dict[title]=content
        return page_dict

    def recordPage(self,section):
        page_dict=self.scrapePage(section)
        for label,data in page_dict.items():
            if label is None:
                if '-tomes' in section:
                    N=section.index('-tomes')
                    section=section[:N]
                elif 'laguz' in section:
                    section='laguz'
                filename=section+'.csv'
            else:
                filename=label+'.csv'
            file=sep.join([self.game_dir,filename])
            data.to_csv(file,index=False,header=False)

    def recordAllPages(self):
        url_list=self.retrieveUrl()
        for url in url_list:
            self.recordPage(url)

class RankFetcher(Angelo):
    def __init__(self):
        x=4

if __name__ == '__main__':
    for game in range(6,10):
        game=str(game)
        dog=Angelo(game)
        dog.recordAllPages()
