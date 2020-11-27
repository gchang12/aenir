from tkinter import *

from aenir2.gui_tools import *
from aenir2.quintessence import Morph
from aenir2.entry_validator import not_my_validator

#   Universal padding for Frame objects
kw={}
pad=4
kw['padx']=pad
kw['pady']=pad
kw['borderwidth']=2

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
        self.root.wm_minsize(width=400,height=500)
        
        menubar=Menu(self.root,tearoff=0)

        guimenu=Menu(menubar,tearoff=0)
        guimenu.add_command(label='Reset',command=self.reset)
        guimenu.add_command(label='Quit',command=self.quit)

        actionmenu=Menu(menubar,tearoff=0)
        actionmenu.add_command(label='Level Up')
        actionmenu.add_command(label='Promote')
        actionmenu.add_command(label='Use Item')

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

    def select_from_list(self,row,column,itemlist,height,label):
        frame=Frame(self.root,**kw)
        frame.grid(row=row,column=column,sticky=N+W+E+S)

        list_var=StringVar(value=itemlist)

        kwargs={
            'master':frame,\
            'listvariable':list_var,\
            'height':height,\
            'width':30
            }
        item_list=Listbox(**kwargs)
        item_list.grid(row=1,column=0)

        item_label=Label(frame,text=label)
        item_label.grid(row=0,column=0,sticky=W)
        return item_list

    def game_select(self):
        row=0
        column=0
        itemlist=tuple(game_title_dict().keys())
        height=len(itemlist)
        label='Game Select'
        x=self.select_from_list(row,column,itemlist,height,label)
        return x

    def unit_select(self,game):
        row=1
        column=0
        height=22
        label='Unit Select'
        itemlist=unit_list(game)
        x=self.select_from_list(row,column,itemlist,height,label)
        return x

    def father_select(self):
        row=0
        column=0
        itemlist=fe4_father_list()
        height=len(itemlist)
        label='Father Select'
        x=self.select_from_list(row,column,itemlist,height,label)
        return x

    def info_box(self,text):
        info_frame=Frame(self.root,**kw)
        info_frame.grid(row=0,column=1,sticky=N+E+W+S)
        info_title=Label(info_frame,text='Info')
        info_title.grid(sticky=N+W,row=0,column=0)
        info_label=Label(info_frame,text=text,wraplength=200,justify=LEFT)
        info_label.grid(row=1,column=0,sticky=N+W)
        return info_label

    def config_box(self):
        cfg_frame=Frame(self.root,**kw)
        cfg_frame.grid(row=1,column=1,sticky=N+W+E+S)
        cfg_title=Label(cfg_frame,text='Config')
        cfg_title.grid(sticky=N+W,row=0,column=0)
        return cfg_frame

    def game_unit_check(self):
        game=self.unit_params['game']
        unit=self.unit_params['unit']
        args=game,unit
        conditions=(
            is_lyndis_league(*args),\
            is_fe4_child(*args),\
            is_hugh(*args),\
            has_hm_bonus(unit),\
            has_auto_bonus(unit)
            )
        return any(conditions)

    def game_unit_init(self):
        gs=self.game_select()
        gs.focus_force()
        gs.select_set(0)
        disable={'state':DISABLED}
        confirm_msg=' Then press Enter in order to confirm your selection.'
        gs_msg='Please select a Fire Emblem game.'
        ib=self.info_box(gs_msg+confirm_msg)

        cb=self.config_box()
        Label(cb,text='Game:').grid(row=1,column=0,sticky=W)
        Label(cb,text='Unit:').grid(row=2,column=0,sticky=W)

        def preview_unit_list(*args):
            title=gs.selection_get()
            game=game_title_dict()[title]
            us=self.unit_select(game)
            us.config(disable)

        preview_unit_list()

        def start_unit_select(*args):
            title=gs.selection_get()
            game=game_title_dict()[title]
            us=self.unit_select(game)
            us.grid({'rowspan':2})
            gs.unbind('<<ListboxSelect>>')
            gs.config(disable)
            self.unit_params.update({'game':game})
            self.display_params.update({'Game':title})

            us_msg='Please select a unit from FE%s.'%game
            ib['text']=us_msg+confirm_msg
            Label(cb,text=title,justify=LEFT).grid(row=1,column=1,sticky=W)

            def confirm_selection(*args):
                us.config(disable)
                new_name=us.selection_get()
                old_name=get_old_name(self.unit_params['game'],new_name)
                self.unit_params.update({'unit':old_name})
                self.display_params.update({'Unit':new_name})

                Label(cb,text=new_name).grid(row=2,column=1)
                final_msg='Please press OK button to proceed. Otherwise, press F5 to restart or Esc to quit.'
                ib['text']=final_msg
                ok_button['state']=ACTIVE
                ok_button.focus()

                sf_kw=kw.copy()
                sf_kw['relief']='sunken'
                stat_frame=Frame(cb,**sf_kw)
                stat_frame.grid(row=3,column=0,columnspan=2)

                if self.game_unit_check():
                    missing_info_msg='Please specify more attribute(s) in order to view stat preview.'
                    label_kw={
                        'text':missing_info_msg,\
                        'justify':LEFT,\
                        'wraplength':100
                        }
                    Label(stat_frame,**label_kw).grid(row=0,column=1)
                else:
                    Label(stat_frame,text='Level:').grid(row=0,column=0)
                    Label(stat_frame,text='Class:').grid(row=1,column=0)

                    y=Morph(**self.unit_params)

                    display_lv=str(y.base_level)
                    display_cls=str(y.current_class())

                    self.display_params.update({'Class':display_cls})
                    self.display_params.update({'Lv':display_lv})
                    
                    Label(stat_frame,text=display_lv).grid(row=0,column=1)
                    Label(stat_frame,text=display_cls).grid(row=1,column=1)

                    game=self.unit_params['game']
                    stat_labels=stat_names(game)
                    count=0

                    Label(stat_frame,text='').grid(row=2,column=1)
                    
                    for name,stat in zip(stat_labels,y.base_stats):
                        stat=str(stat)
                        name+=':'
                        row=count+3
                        Label(stat_frame,text=name).grid(column=0,row=row)
                        Label(stat_frame,text=stat).grid(column=1,row=row)
                        count+=1

            us.focus()
            us.select_set(0)
            us.bind('<Return>',confirm_selection)

        gs.bind('<<ListboxSelect>>',preview_unit_list)
        gs.bind('<Return>',start_unit_select)

        def end_init(*args):
            ok_button['state']=DISABLED
            ok_button.unbind('<Return>')
            ib['text']=''
            for child in self.root.winfo_children():
                if type(child) == Menu:
                    continue
                for grandkid in child.winfo_children():
                    if type(grandkid) == Listbox:
                        child.destroy()
                        break
                    if len(grandkid.winfo_children()) > 0:
                        grandkid.destroy()
                        break

        ok_frame=Frame(self.root,**kw)
        ok_frame.grid(row=2,column=1,sticky=S)

        ok_cfg={
            'text':'OK',\
            'state':DISABLED,\
            'command':end_init,\
            'width':30,\
            'justify':LEFT
            }

        ok_button=Button(ok_frame,**ok_cfg)
        ok_button.grid(sticky=S)
        ok_button.bind('<Return>',end_init)

    def __call__(self):
        self.load_menu()
        self.game_unit_init()

if __name__ == '__main__':
    x=Aenir()
    x()
