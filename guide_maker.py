from episode_guide.datetime_functions import *
from episode_guide.file_operations import filelistOrganizer, lineCounter
from episode_guide.quote_fixer import fix_file_quote
from episode_guide.scolder import messageWriter
from episode_guide.string_operations import replace_reserved_chars
from episode_guide.title_operations import titleExtractor
from episode_guide.web_scraper import shortSeriesTableMaker, seriesTableMaker
from episode_guide.program_dict import ProgramDict

import pandas as pd

from shutil import move, rmtree

from os import mkdir, walk, system, getcwd, chdir
from os.path import exists, sep

class GuideMaker:
    def __init__(self,program_name):
        pdict=ProgramDict()
        if program_name in pdict.keys():
            self.episode_list=pdict[program_name]
        else:
            program_file=sep.join(('.','metadata','my-programs.csv'))
            message=(
                'The program:',\
                program_name,\
                'is not in the list of known television programs.',\
                'A list of currently valid names is given above. You have two options:',\
                '1. Select the appropriate option from the list.',\
                '2. Append the name and Wikipedia URL to its episode-list to:',\
                program_file,
                )
            for p in pdict.keys():
                print(p)
            messageWriter(message)
        self.folder_title=titleExtractor(self.episode_list,True)
        self.true_title=titleExtractor(self.episode_list,False)
        pathPointer=lambda name: sep.join(('.',name,self.folder_title))
        self.table_dir=pathPointer('tables')
        self.text_dir=pathPointer('text')
        title_length=len(self.folder_title)
        self.output_dir=sep.join(('.','output'))
        self.metadata=sep.join(('.','metadata'))
        self.main_dirs=(
            self.table_dir[:-title_length],\
            self.text_dir[:-title_length],\
            self.output_dir
            )
        self.log=sep.join((self.metadata,'unicode-dict.csv'))

    def makeAllFolders(self):
        folders=(*self.main_dirs,self.table_dir,self.text_dir)
        for folder in folders:
            if not exists(folder):
                mkdir(folder)

    def eraseAllFolders(self):
        to_remove=self.table_dir,self.text_dir
        for folder in to_remove:
            if not exists(folder):
                continue
            rmtree(folder)

    def saveSeasonData(self,season,file):
        data=pd.DataFrame(season).transpose()
        if data.empty:
            return
        file=sep.join((self.table_dir,file+'.csv'))
        data.to_csv(file)

    def getSeriesData(self):
        try:
            all_seasons=seriesTableMaker(self.episode_list)
            all_seasons=tuple(all_seasons)
        except Exception:
            all_seasons=shortSeriesTableMaker(self.episode_list)
        return all_seasons

    def saveSeriesData(self):
        all_seasons=self.getSeriesData()
        for n,season in enumerate(all_seasons,1):
            n=str(n)
            self.saveSeasonData(season,n)

    def logUnicodeText(self,text):
        log_file=self.log
        logged=list()
        kw={
            'encoding':'utf-8'
            }
        if exists(log_file):
            mode='a'
            with open(log_file,'r',**kw) as rfile:
                for line in rfile.readlines():
                    line=line.split(',')
                    line=line[0]
                    logged.append(line)
        else:
            mode='w'
        with open(log_file,mode,**kw) as xfile:
            for word in text:
                if not word.isascii() and word not in logged:
                    xfile.write(word+',\n')
                    logged.append(word)

    def outputFile(self,filename):
        return sep.join([self.text_dir,filename])

    def scoldUser(self):
        scold=False
        if not exists(self.table_dir):
            scold=True
        else:
            for x,y,hasfiles in walk(self.table_dir):
                if not hasfiles:
                    scold=True
        if scold:
            message=(
                    'No data has yet been scraped for %s.'%self.true_title,\
                    'Please web-scrape the data first, then re-run the script.',\
                    'Try running the webScrape method.'
                    )
            messageWriter(message)

    def scoldUserAgain(self):
        scold=False
        for x,y,hasfiles in walk(self.text_dir):
            if not hasfiles:
                scold=True
        if scold:
            message=(
                'Text has not been scraped for %s.'%self.true_title,\
                'Please compile text with the compileText method.'
                )
            messageWriter(message)

    def writeText(self,column):
        save_file=column+'.txt'
        save_file=self.outputFile(save_file)
        missing_columns=dict()
        with open(save_file,'w',encoding='utf-8') as wfile:
            for x,y,files in walk(self.table_dir):
                files=filelistOrganizer(files)
                for file in files:
                    file=self.table_dir,file
                    file=sep.join(file)
                    data=pd.read_csv(file,index_col=0)
                    if column not in data.columns:
                        if file in missing_columns.keys():
                            missing_columns[file].append(column)
                        else:
                            missing_columns[file]=[column]
                        continue
                    for n,text in enumerate(data.loc[:,column],1):
                        text=str(text)
                        text=replace_reserved_chars(text,self.metadata)
                        if not text.isascii():
                            self.logUnicodeText(text)
                        if '\n' in text:
                            text=text[:text.index('\n')]
                        wfile.write(text+'\n')
        if missing_columns:
            for key,val in missing_columns.items():
                print(key,val)
            message=(
                'There were columns missing from some episode-tables.',\
                'Please check the files listed above for more details.'
                )
            messageWriter(message)

    def writeAllText(self):
        columns='title','date','summary'
        initial_count=lineCounter(self.log)
        for column in columns:
            self.writeText(column)
        final_count=lineCounter(self.log)
        diff=final_count-initial_count
        if diff > 0:
            message=(
                '%d new unicode character(s) have been encountered.'%diff,\
                'Please revise the appropriate log accordingly:',\
                self.log,\
                'For each character, write its TeX equivalent.'
                )
            messageWriter(message)

    def readSeriesData(self):
        for x,y,files in walk(self.table_dir):
            files=filelistOrganizer(files)
            for file in files:
                file=sep.join((self.table_dir,file))
                data=pd.read_csv(file,index_col=0)
                yield data

    def recordSeasonLength(self):
        save_file=self.outputFile('season_lengths.txt')
        total=0
        with open(save_file,'w') as wfile:
            for table in self.readSeriesData():
                line_count=len(table)
                total+=line_count
                line_count=str(total)+'\n'
                wfile.write(line_count)

    def fixQuotes(self):
        file=self.outputFile('summary.txt')
        tex_file=self.outputFile('tex-summary.txt')
        fix_file_quote(file,tex_file,'.')

    def fixDates(self):
        file=self.outputFile('date.txt')
        tex_file=self.outputFile('tex-date.txt')
        if exists(tex_file):
            message=(
                'The file containing the air-dates already exists.',\
                'It is not recommended to overwrite it, if you\'ve edited it.',\
                'In order to rewrite the file, please rerun the program after deleting:',\
                tex_file,\
                'To validate your manual corrections to the file, use the checkDates method.'
                )
            messageWriter(message)
        old_dates=list()
        with open(file,'r') as rfile:
            for line in rfile.readlines():
                line=line.strip()
                old_dates.append(line)
        bad_dates=monthRewriter(tex_file,old_dates)
        if bad_dates:
            for key,val in bad_dates.items():
                print(key,val)
            message=(
                'There were some bad dates in the .txt file:',\
                tex_file,\
                'The errors and their line numbers are listed above.',\
                'Please correct the errors shown above to proceed.',\
                'Check your work with the checkDates method.'
                )
            messageWriter(message)

    def webScrape(self):
        self.makeAllFolders()
        self.saveSeriesData()

    def checkDates(self):
        file=self.outputFile(r'tex-date.txt')
        bad_lines=dict()
        with open(file) as rfile:
            for n,line in enumerate(rfile.readlines(),start=1):
                line=line.strip()
                if not dateValidator(line):
                    bad_lines[n]=line
        if bad_lines:
            for item in bad_lines.items():
                print(item)
            message=(
                'There were still some bad dates in tex-date.txt.',\
                'Please find the errors in the line numbers above and fix them accordingly.',\
                'Remember that the date must be of the form: (month) (day), (full-year)',\
                'For example:',\
                todaysDate()
                )
            messageWriter(message)
        else:
            message=(
                'Your dates are all valid. It is now safe to call the GuideMaker object.'
                )
            messageWriter(message,error=False)

    def compileText(self):
        self.scoldUser()
        self.writeAllText()
        self.recordSeasonLength()
        self.fixQuotes()
        self.fixDates()

    def recordProgramName(self):
        filename='program-name.txt'
        filename=sep.join((self.output_dir,filename))
        with open(filename,'w') as wfile:
            write_val=self.folder_title,self.true_title
            write_val='\n'.join(write_val)
            wfile.write(write_val)

    def typeset(self):
        self.scoldUser()
        self.scoldUserAgain()
        self.recordProgramName()
        guide_loc=sep.join(('.','output'))
        pwd=getcwd()
        chdir(guide_loc)
        guide='guide.tex'
        system("pdflatex %s"%guide)
        src=guide[:-3]+'pdf'
        if not exists(src):
            message='The .pdf file was not successfully compiled.',\
                    'Please e-mail the imbecile what wrote this program, or better yet, fix it yourself.'
            messageWriter(message)
        system("pdflatex %s"%guide)
        dst='..','text',self.folder_title,'guide.pdf'
        dst=sep.join(dst)
        move(src,dst)
        chdir(pwd)
        message='Your .pdf file has been saved to:',dst[1:]
        messageWriter(message,error=False)

    def __call__(self):
        if not exists(self.text_dir):
            self.webScrape()
        elif not exists(self.outputFile('tex-date.txt')):
            self.compileText()
        else:
            self.checkDates()
            self.typeset()


def make_guide(tv_program,first_time=True):
    y=GuideMaker(x)
    if first_time:
        y.eraseAllFolders()
        y.webScrape()
        y.compileText()
        y.checkDates()
        y.typeset()
    else:
        y()

if __name__ == '__main__':
    x='My So-Called Life'
    make_guide(x)
