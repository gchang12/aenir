from tkinter import *
from tkinter import font, filedialog
from aenir2.entry_validator import not_my_validator

from os import mkdir, getcwd
from os.path import exists, sep

from PIL import ImageGrab; from win32gui import *#GetWindowRect
from pyscreenshot import grab
from pyautogui import screenshot

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

def find_img_loc():
    k=1
    folder=sep.join((getcwd(),'screenshots'))
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

def save_image(root):
    #   https://stackoverflow.com/questions/9886274/how-can-i-convert-canvas-content-to-an-image
    if not exists('screenshots'):
        mkdir('screenshots')
    new_geometry='400x400+400+200'
    root.geometry(new_geometry)
    root.update()
    HWND = root.winfo_id()  # get the handle of the canvas
    rect = GetWindowRect(HWND)  # get the coordinate of the canvas
    im = ImageGrab.grab(rect)  # get image of the current location
    filename=find_img_loc()
    if not filename:
        return
    else:
        im.save(filename,format='png')

def save_image2(root):
    geometry=root.wm_geometry()
    location=geometry.split('+')
    dimension=location[0].split('x')
    xpos=int(location[1])+8
    ypos=int(location[2])+4
    xlen=int(dimension[0])+2
    ylen=int(dimension[1])+60
    #root.update()
    bbox=(xpos,ypos,xpos+xlen,ypos+ylen)
    im=grab(bbox=bbox)
    filename=find_img_loc()
    if not filename:
        return
    else:
        im.save(filename,format='png')


def save_image3(root):
    new_geometry='400x400+400+200'
    root.geometry(new_geometry)
    root.update()
    HWND = root.winfo_id()  # get the handle of the canvas
    im=screenshot(region=(800,600,400,200))
    filename=find_img_loc()
    if not filename:
        return
    else:
        im.save(filename,format='png')


if __name__ == '__main__':
    root=Tk()
    root.geometry('400x400+400+200')
    #root.update()
    print(root.wm_geometry())
    Label(root,text='Sample text here').grid(row=1)
    Label(root,text='More sample text...').grid(row=2)
    Label(root,text='One more for the road.').grid(row=3)
    save_image2(root)
    root.destroy()
