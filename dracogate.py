from tkinter import *

def show_preview(active_wid,widget_call,value_call):
    def preview(*args):
        x=active_wid.selection_get()
        x=value_call(x)
        static_wid=widget_call(x)
        static_wid.config({'state':DISABLED,'takefocus':False})
    return preview

def next_widget(wid,wid_call,val_call,convert):
    def to_next(*args):
        wid.config({'state':DISABLED})
        val=convert(val_call())
        next_wid=wid_call(val)
        next_wid.focus()
        wid.unbind('<<ListboxSelect>>')
    return to_next,next_wid

from aenir2.gui_tools import *
from aenir2.quintessence import Morph

class Aenir:
    def __init__(self):
        self.unit_params={}
        self.hm_params={}
        self.auto_params={}
        self.misc_params={}
        self.display_params={}
        self.session_history=[]
        self.info_variables=self.unit_params,\
                             self.hm_params,\
                             self.auto_params,\
                             self.misc_params,\
                             self.display_params,\
                             self.session_history
        self.my_unit=None

    def load_menu(self):
        self.root=Tk()
        self.root.title('Aenir')
        
        menubar=Menu(self.root,tearoff=0)
        
        guimenu=Menu(menubar,tearoff=0)
        guimenu.add_command(label='Reset',command=self.reset)
        guimenu.add_command(label='Quit',command=self.quit)

        actionmenu=Menu(menubar,tearoff=0)
        actionmenu.add_command(label='Level Up')#,command=[level-up sidebar])
        actionmenu.add_command(label='Promote')#,command=[promote sidebar])
        actionmenu.add_command(label='Use Item')#,command=[item sidebar])

        viewmenu=Menu(menubar,tearoff=0)
        viewmenu.add_command(label='History')
        viewmenu.add_command(label='Comparison')

        menubar.add_cascade(label='Main',menu=guimenu)
        menubar.add_cascade(label='Edit',menu=actionmenu,state=DISABLED)
        menubar.add_cascade(label='View',menu=guimenu,state=DISABLED)

        self.root.config(menu=menubar)

        self.root.bind_all('<Escape>',lambda *args: self.quit())
        self.root.bind_all('<F5>',lambda *args: self.reset())

    def reset(self):
        self.quit()
        self.__call__()

    def quit(self):
        for var in self.info_variables:
            var.clear()
        self.my_unit=None
        self.root.destroy()

    def __bool__(self):
        #   Tells user if factory-resetted via quit call
        return self.my_unit is None and not any(self.info_variables)

    def select_from_list(self,row,column,itemlist,height):
        kw={}
        k=5
        kw['padx']=k
        kw['pady']=k
        kw['borderwidth']=2
        frame=Frame(self.root,**kw)
        frame.grid(row=row,column=column)

        list_var=StringVar(value=itemlist)

        kwargs={
            'master':frame,\
            'listvariable':list_var,\
            'height':height
            }
        item_list=Listbox(**kwargs)
        item_list.grid()
        return item_list

    def append_unit_param(self,val_call,dval_call,key):
        val=val_call()
        dval=dval_call(val)
        self.unit_params.update({key:val})
        if key == 'lyn_mode':
            key='Lyn Mode'
        else:
            key=key.capitalize()
        self.display_params.update({key:dval})

    def game_select(self,row,column):
        itemlist=tuple(game_title_dict().keys())
        gs_list=self.select_from_list(row,column,itemlist,6)
        val_call=gs_list.selection_get
        dval_call=lambda title: game_title_dict()[title]
        key='game'
        kw={
            'wid_call':self.unit_select,\
            'row':1,\
            'column':0
            }
        self.bind_append(gs_list,val_call,dval_call,key)
        return gs_list

    def bind_append(self,wid,val_call,dval_call,key):
        f=lambda *args: self.append_unit_param(val_call,dval_call,key)
        wid.bind('<Return>',f)

    def unit_select(self,row,column,game):
        itemlist=character_list(game)
        us_list=self.select_from_list(row,column,itemlist,10)
        val_call=us_list.selection_get
        dval_call=lambda new_name: get_old_name(game,new_name)
        key='unit'
        self.bind_append(us_list,val_call,dval_call,key)
        return us_list

    def info_box(self,text=''):
        kw={
            'row':0,\
            'column':1,\
            'relief':'sunken'
            }
        info_frame=Frame(self.root)
        info_frame.grid(row,**kw)
        info_label=Label(info_frame,text=text)
        info_label.grid()

    def settings_display(self):
        kw={
            'row':1,\
            'column':1,\
            'relief':'sunken'
            }
        opt_frame=Frame(self.root)
        opt_frame.grid(**kw)

        opt_labels=

    def __call__(self):
        self.load_menu()
        gs=self.game_select(1,0)
        gs.focus()
        us_call=lambda game: self.unit_select(3,0,game)
        us=us_call('4')
        us['state']=DISABLED
        title_to_num=lambda title: game_title_dict()[title]
        gs.bind('<<ListboxSelect>>',show_preview(gs,us_call,title_to_num))
        func,us=next_widget(gs,us_call,gs.selection_get,title_to_num)
        bind_kw={
            'sequence':'<Return>',\
            'func':func
            }
        gs.bind(**bind_kw)
        us.bind(sequence='<Return>',func=lambda *args: print(45),add=True)
        #   Main routine here; save for very end.

if __name__ == '__main__':
    x=Aenir()
    x()
