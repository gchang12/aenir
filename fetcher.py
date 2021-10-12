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

    def gatherRows(self,tr,cell):
        assert cell in ('td','th')
        rows=list()
        if cell == 'td':
            unwanted='th'
            string_test=lambda x: False
        elif cell == 'th':
            unwanted='td'
            string_test=lambda x: x in rows
        # If unwanted tag is in content row, set flag to True
        mixed_tr=False
        if tr.find(unwanted) is not None:
            mixed_tr=True
        # Iterating over empty list if tag is not found
        for tag in tr.find_all(cell):
            text=tag.text
            text=text.strip()
            if cell == 'td':
                if text.isnumeric():
                    text=int(text)
            if string_test(text):
                break
            else:
                rows.append(text)
        # If both row is non-empty and th tag is found, then raise error
        assert not (rows and mixed_tr)
        return rows

    def scrapeTable(self,table):
        data_list=list()
        for tr in table.find_all('tr'):
            # If data_list is empty, then it is the first row
            is_first_row=not data_list
            if is_first_row:
                # If row has no td tags and has th tags, then it is a header row
                is_header_row=tr.find('td') is None and tr.find('th') is not None
                if is_header_row:
                    headers=self.gatherRows(tr,'th')
                    data_list.append(headers)
                else:
                    # If it is not a header row, stop interpreter
                    message='First row is not a header row.'
                    print(message,table)
                    raise Exception
                continue
            row=self.gatherRows(tr,'td')
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
