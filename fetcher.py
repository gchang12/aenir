from bs4 import BeautifulSoup
from requests import get

from os import mkdir
from os.path import sep, exists

import pandas as pd

from aenir2.data_fetcher import get_nickname

class Fetcher:
    def __init__(self,game,folder_name):
        self.root='https://serenesforest.net'
        self.game=game
        self.title=get_nickname(game)
        self.main_dir=sep.join(['.',folder_name])
        pathPointer=lambda x: sep.join([self.main_dir,x])
        self.game_dir=pathPointer('fe'+game)

    def createDir(self):
        dirs=self.main_dir,self.game_dir
        for d in dirs:
            if not exists(d):
                mkdir(d)

    def joinUrl(self,section,subsection):
        url=[self.root,self.title]
        if section is None:
            url.append('')
        else:
            portals=section,subsection
            for portal in portals:
                url.append(portal)
        return '/'.join(url)

    def outputFile(self,filename):
        return sep.join([self.game_dir,filename])

    def gatherHeaders(self,tr):
        headers=list()
        for th in tr.find_all('th'):
            header=th.text
            header=header.strip()
            if header not in headers:
                headers.append(header)
            else:
                break
        return headers

    def gatherContents(self,tr):
        row=list()
        mixed_tr=False
        if tr.find('th') is not None:
            # If th tag is in content row, set flag to True
            mixed_tr=True
        # Iterating over empty list if td is not found
        for td in tr.find_all('td'):
            cell=td.text
            if cell.isnumeric():
                cell=int(cell)
            row.append(cell)
        # If both row is non-empty and th tag is found, then raise error
        # It could be the case that row has neither td nor th tags
        # - no error raised; row is skipped
        assert not (row and mixed_tr)
        return row

    def scrapeTable(self,table):
        data_list=list()
        for tr in table.find_all('tr'):
            if not data_list:
                if tr.find('td') is None and tr.find('th') is not None:
                    # Asserting that the first row is a header row
                    headers=self.gatherHeaders(tr)
                    data_list.append(headers)
                else:
                    message='First row is not a header row.'
                    print(message,table)
                    raise Exception
                continue
            row=self.gatherContents(tr)
            if row:
                data_list.append(row)
        assert data_list
        return data_list

    def scrapePage(self,section,parser='html.parser'):
        url=self.joinUrl(section=section)
        soup=BeautifulSoup(get(url).text,parser)
        kw={'index':None}
        for table in soup.find_all('table'):
            table=self.scrapeTable(table)
            header=table[0]
            kw['columns']=header
            kw['data']=table
            data=pd.DataFrame(**kw)
            yield data

    def recordPage(self,section):
        page_dict=self.scrapePage(section)
        filename=section+'.csv'
        file=self.outputFile(filename)
        kw={'index':False,'header':False}
        for data in page_list:
            data.to_csv(file,**kw)
