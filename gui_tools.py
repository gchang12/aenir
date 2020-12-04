from tkinter import *
from tkinter import font
from aenir2.entry_validator import not_my_validator

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

if __name__ == '__main__':
    root=Tk()
    f=lambda : print('OK')
    g=lambda : print('Cancel')
    yes,no=buttonPair(root,f,g)
    h=lambda *args: yes.config({'state':NORMAL})
    k=numericalEntry(root,h)
    root.mainloop()
