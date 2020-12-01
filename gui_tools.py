from tkinter import font,LabelFrame,StringVar,Listbox,N,S,W,E,Scrollbar,Label,Button,NORMAL,DISABLED

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

def select_from_list(master,itemlist,height,add_scrollbar=False):
    list_var=StringVar(value=itemlist)

    kwargs={
        'master':master,\
        'listvariable':list_var,\
        'height':height,\
        'width':30
        }
    item_list=Listbox(**kwargs)
    item_list.grid(column=0,sticky=N+W+S,row=0)

    if add_scrollbar:
        scrollbar=Scrollbar(master)
        scrollbar.grid(column=1,sticky=N+S,rowspan=2,row=0)
        scrollbar.config(command=item_list.yview)
        item_list['yscrollcommand']=scrollbar.set

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
        number=2
        if x == 'Prior':
            target=current_index - height
            if target < 0:
                target=0
            number=-number
        else:
            target=current_index+height
            if target > length:
                target=length
        listbox.yview_scroll(number,'units')
    else:
        return
    listbox.activate(target)
    listbox.select_set(target)
    listbox.select_anchor(target)
    

def bind_listbox_shortcuts(listbox):
    keys='<End>','<Home>','<Prior>','<Next>'
    bind_to_shortcuts=lambda *args: listbox_jump(listbox,*args)
    for key in keys:
        listbox.bind(key,bind_to_shortcuts)

def wideButton(master,text,command,row,width=23,height=2,column=None,state=NORMAL):
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
    if type(column) == int:
        g['column']=column

    button=Button(**d)
    button.grid(**g)
    button.bind('<Return>',command)
    return button

if __name__ == '__main__':
    x=4
