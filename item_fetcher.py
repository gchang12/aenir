from bs4 import BeautifulSoup
from requests import get

from os import mkdir
from os.path import sep, exists

import pandas as pd

from aenir2.data_fetcher import get_nickname

class Angelo:
    def __init__(self,game):
        self.root='https://serenesforest.net'
        self.game=game
        self.title=get_nickname(game)
        self.main_dir=sep.join(['.','weapon_data'])
        pathPointer=lambda x: sep.join([self.main_dir,x])
        self.game_dir=pathPointer('fe'+game)
        self.data_file=pathPointer('data-locations.txt')

    def createDir(self):
        dirs=self.main_dir,self.game_dir
        for d in dirs:
            if not exists(d):
                mkdir(d)

    def joinUrl(self,section=None):
        url=[self.root,self.title]
        if section is None:
            url.append('')
        else:
            portals='inventory',section
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

    def scrapePage(self,section):
        if (self.game,section) in [('5','axes'),('6','anima-tomes')]:
            parser='html5lib'
        else:
            parser='html.parser'
        url=self.joinUrl(section=section)
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

    def outputFile(self,filename):
        return sep.join([self.game_dir,filename])

    def recordPage(self,section):
        page_dict=self.scrapePage(section)
        kw={'index':False,'header':False}
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
            file=self.outputFile(filename)
            data.to_csv(file,**kw)

    def recordAllPages(self):
        url_list=self.retrieveUrl()
        for url in url_list:
            self.recordPage(url)

def save_all():
    for n in range(4,10):
        game=str(n)
        dog=Angelo(game)
        dog.recordAllPages()

if __name__ == '__main__':
    save_all()
