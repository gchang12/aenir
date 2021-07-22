from tkinter import *
from tkinter import font, filedialog
from aenir2.entry_validator import not_my_validator

from os import mkdir, getcwd
from os.path import exists, sep

from pyscreenshot import grab

from datetime import datetime

def underline_font(myLabel):
    my_font=font.Font(myLabel,myLabel.cget('font'))
    my_font.configure(underline=True)
    myLabel.configure(font=my_font)

def set_mainframe(row,column,width,height,rowspan=1,text=' '):
    kw={
        'padx':4,\
        'pady':4,\
        'borderwidth':2,\
        'width':width,\
        'height':height,\
        'relief':'sunken',\
        'text':text
        }
    frame=LabelFrame(**kw)
    frame.grid_propagate(0)
    grid_kw={
        'padx':10,\
        'pady':0
        }
    frame.grid(row=row,column=column,rowspan=rowspan,**grid_kw)
    return frame

def select_from_list(master,itemlist,height,add_scrollbar=False,width=30,get_var=False,scroll_col=1):
    list_var=StringVar(value=itemlist)

    kwargs={
        'master':master,\
        'listvariable':list_var,\
        'height':height,\
        'width':width
        }
    item_list=Listbox(**kwargs)
    item_list.grid(column=0,sticky=N+W+S,row=0)

    if add_scrollbar:
        scrollbar=Scrollbar(master)
        scrollbar.grid(column=scroll_col,sticky=N+S,row=0)
        scrollbar.config(command=item_list.yview)
        item_list['yscrollcommand']=scrollbar.set
    if get_var:
        return item_list,list_var
    return item_list

def anakin(frame):
    assert type(frame) == LabelFrame
    temple=frame.winfo_children()
    for youngling in temple:
        youngling.destroy()

def listbox_jump(listbox,*args):
    x=args[0].keysym
    current_index=listbox.curselection()[0]
    height=listbox['height']
    length=listbox.size()-1
    listbox.selection_clear(0,length)
    if x in ('End','Home'):
        if x == 'End':
            target=length
        else:
            target=0
        number=target-current_index
        listbox.yview_scroll(number,'units')
    elif x in ('Prior','Next'):
        if x == 'Prior':
            target=current_index - height
            if target < 0:
                target=0
        else:
            target=current_index+height
            if target > length:
                target=length
    else:
        return
    listbox.activate(target)
    listbox.see(target)
    listbox.select_set(target)
    

def bind_listbox_shortcuts(listbox):
    keys='<End>','<Home>'
    #keys+=('<Prior>','<Next>')
    bind_to_shortcuts=lambda *args: listbox_jump(listbox,*args)
    for key in keys:
        listbox.bind(key,bind_to_shortcuts)
    return keys

def wideButton(master,text,command,row,width=23,height=2,column=0,state=NORMAL):
    d={}
    d['master']=master
    d['text']=text
    d['width']=width
    d['height']=height
    d['command']=command
    d['state']=state

    g={}
    g['sticky']=N+S+E+W
    g['ipadx']=10
    g['ipady']=10
    g['row']=row
    g['columnspan']=2
    g['column']=column

    button=Button(**d)
    button.grid(**g)
    return button

def updateButton(button,text,command,state=NORMAL):
    cfg={
        'text':text,\
        'command':command,\
        'state':state
        }
    button.config(cfg)

def append_listbox_shortcuts(listbox,func=None):
    keys=bind_listbox_shortcuts(listbox)
    if not callable(func):
        return
    else:
        listbox.bind('<<ListboxSelect>>',func)
        for key in keys:
            listbox.bind(key,func,add=True)

def buttonPair(master,command1,command2,width=10,height=0,pad=10,text1='Confirm',text2='Cancel'):
    b={}
    b['master']=master
    b['width']=width
    b['height']=height

    b1=b.copy()

    b1['text']=text1
    b1['state']=DISABLED
    b1['command']=command1

    okButton=Button(**b1)

    b2=b.copy()

    b2['text']=text2
    b2['state']=NORMAL
    b2['command']=command2
    
    rtnButton=Button(**b2)

    bg={}

    bg['sticky']=E+W
    bg['ipadx']=pad
    bg['ipady']=pad

    okButton.grid(row=1,column=0,**bg)
    rtnButton.grid(row=1,column=1,**bg)

    return okButton,rtnButton

def numericalEntry(master):
    number=StringVar()
    entry=Entry(master,textvariable=number,validate='key')
    entry['vcmd']=(entry.register(not_my_validator), '%P', '%d')
    entry.grid(row=0,column=0,columnspan=2)
    entry.focus()
    return number,entry

def datetime_name():
    now=datetime.now()
    today=now.date()
    time=now.time()
    today=str(today)
    time=str(time)
    time=time.replace(':','')
    time=time.replace('.','_')
    return today,time

def find_img_loc(dt=False):
    k=1
    folder=sep.join((getcwd(),'screenshots'))
    if dt:
        today,time=datetime_name()
        initial_file='_'.join((today,time))
    else:
        initial_file='screenshot'+str(k)
        filename=lambda x: sep.join((folder,x+'.png'))
        while exists(filename(initial_file)):
            k+=1
            n=len(str(k-1))
            initial_file=initial_file[:-n]+str(k)
    kw={
        'initialfile':initial_file,\
        'defaultextension':'png',\
        'initialdir':folder,\
        'filetypes':[('.png files only','*.png')]
        }
    filename=filedialog.asksaveasfilename(**kw)
    return filename

def save_image(im,dt=False):
    if not exists('screenshots'):
        mkdir('screenshots')
    filename=find_img_loc(dt=dt)
    if not filename:
        return
    else:
        im.save(filename,format='png')

def get_geometry(root):
    geometry=root.winfo_geometry()
    position=geometry.split('+')
    dimension=position[0].split('x')
    xlen=dimension[0]
    ylen=dimension[1]
    xpos=position[1]
    ypos=position[2]
    geo_list=(xpos,ypos,xlen,ylen)
    geometry=()
    for n,g in enumerate(geo_list):
        g=int(g)
        if n > 1:
            h=int(geo_list[n-2])
            if n == 2:
                add=175
            elif n == 3:
                add=105
            g+=h+add
        else:
            if n == 0:
                add=105
            elif n == 1:
                add=35
            g+=add
        geometry+=(g,)
    return geometry

def save_image_plus(root,dt=False):
    root.update()
    geometry=root.winfo_geometry()
    position=geometry.split('+')
    dimension=position[0].split('x')
    xlen=dimension[0]
    ylen=dimension[1]
    xpos=position[1]
    ypos=position[2]
    geo_list=(xpos,ypos,xlen,ylen)
    geometry=()
    k=1.25
    for n,g in enumerate(geo_list):
        g=int(g)
        g=k*g
        if n == 0:
            g+=10
        g=int(g)
        if n>1:
            h=geo_list[n-2]
            h=int(h)
            h=k*h
            k*=1.075
            h=int(h)
            geometry+=(g+h,)
        else:
            geometry+=(g,)
    im=grab(bbox=geometry)
    save_image(im,dt=dt)

if __name__ == '__main__':
    root=Tk()
    root.geometry('300x200+400+100')
    Label(root,text='Yabba dabba doo').grid()
    save_image1(root)
