from tkinter import *

from aenir2.gui_tools import *
from aenir2.quintessence import Morph
from aenir2.entry_validator import not_my_validator

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
        self.padding={
            'padx':4,\
            'pady':4,\
            'borderwidth':2
            }
        #   Declared in methods
        self.root=None
        self.ib=None
        self.cb=None
        self.stat_frame=None

    def load_menu(self,win_width=428,win_height=560):
        self.root=Tk()
        self.root.title('Aenir')
        self.root.wm_minsize(width=win_width,height=win_height)

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
        #   Declared in methods
        self.root.destroy()
        self.root=None
        self.ib=None
        self.cb=None
        self.stat_frame=None

    def __bool__(self):
        return self.my_unit is None and not any(self.info_variables)

    def select_from_list(self,row,column,itemlist,height,label):
        frame=Frame(self.root,**self.padding)
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

        underline_font(item_label)
        
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
        info_frame=Frame(self.root,**self.padding)
        info_frame.grid(row=0,column=1,sticky=N+E+W+S)
        info_title=Label(info_frame,text='Info')

        underline_font(info_title)
        
        info_title.grid(sticky=N+W,row=0,column=0)
        info_label=Label(info_frame,text=text,wraplength=200,justify=LEFT)
        info_label.grid(row=1,column=0,sticky=N+W)
        return info_label

    def config_box(self):
        cfg_frame=Frame(self.root,**self.padding)
        cfg_frame.grid(row=1,column=1,sticky=N+W+E+S)
        cfg_title=Label(cfg_frame,text='Confirm')

        underline_font(cfg_title)

        cfg_title.grid(sticky=N+W,row=0,column=0)
        return cfg_frame

    def game_unit_check(self):
        d=self.unit_params
        conditions=(
            #   Checkbutton
            is_lyndis_league(**d),\
            #  Listbox
            is_fe4_child(**d),\
            #   Entry
            is_hugh(**d),\
            #   Checkbutton/Listbox
            has_hm_bonus(**d),\
            #   Checkbutton/Listbox
            has_auto_bonus(**d)
            )
        return any(conditions)

    def label_array(self,frame,stat_labels,stat_values,display_cls,display_lv):
        kw={}
        kw['relief']='sunken'
        kw.update(self.padding)

        st={}
        st['sticky']=N+S+E

        lc_frame=Frame(frame,**kw)
        lc_frame.grid(row=0,**st)
        Label(lc_frame,text='Class:').grid(row=0,column=0)
        Label(lc_frame,text='Level:').grid(row=1,column=0)

        Label(lc_frame,text=display_cls).grid(row=0,column=1)
        Label(lc_frame,text=display_lv).grid(row=1,column=1)

        game=self.unit_params['game']
        stat_labels=stat_names(game)

        num_frame=Frame(self.stat_frame,**kw)
        num_frame.grid(row=1,**st)

        row=0

        for name,stat in zip(stat_labels,stat_values):
            stat=str(stat)
            name+=':'
            Label(num_frame,text=name).grid(column=0,row=row)
            Label(num_frame,text=stat).grid(column=1,row=row)
            row+=1

    def game_unit_init(self):
        gs=self.game_select()
        gs.focus_force()
        gs.select_set(0)
        disable={'state':DISABLED}
        confirm_msg=' Then press Enter in order to confirm your selection.'
        gs_msg='Please select a Fire Emblem game.'
        self.ib=self.info_box(gs_msg+confirm_msg)

        self.cb=self.config_box()
        Label(self.cb,text='Game:').grid(row=1,column=0,sticky=W)
        Label(self.cb,text='Unit:').grid(row=2,column=0,sticky=W)

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
            gs.unbind('<<ListboxSelect>>')
            gs.config(disable)
            self.unit_params.update({'game':game})
            self.display_params.update({'Game':title})

            us_msg='Please select a unit from FE%s.'%game
            self.ib['text']=us_msg+confirm_msg
            Label(self.cb,text=title,justify=LEFT).grid(row=1,column=1,sticky=W)

            def confirm_selection(*args):
                us.config(disable)
                new_name=us.selection_get()
                old_name=get_old_name(self.unit_params['game'],new_name)
                self.unit_params.update({'unit':old_name})
                self.display_params.update({'Unit':new_name})

                Label(self.cb,text=new_name).grid(row=2,column=1)
                final_msg='Please press OK button to proceed. Otherwise, press F5 to restart or Esc to quit.'
                self.ib['text']=final_msg
                ok_button['state']=ACTIVE
                ok_button.focus()

                self.stat_frame=Frame(self.cb,**self.padding)
                self.stat_frame.grid(row=3,column=0,columnspan=2)

                y=Morph(**self.unit_params)

                display_lv=str(y.base_level)
                display_cls=str(y.current_class())

                self.display_params.update({'Class':display_cls})
                self.display_params.update({'Level':display_lv})

                if self.game_unit_check():
                    missing_info_msg='Please specify more attribute(s) in order to view stat preview.'
                    label_kw={
                        'text':missing_info_msg,\
                        'justify':LEFT,\
                        'wraplength':100
                        }
                    Label(self.stat_frame,**label_kw).grid(row=0,column=1)
                else:
                    stat_labels=stat_names(self.unit_params['game'])
                    stat_values=y.base_stats
                    self.label_array(self.stat_frame,stat_labels,stat_values,display_cls,display_lv)

            us.focus()
            us.select_set(0)
            us.bind('<Return>',confirm_selection)

        gs.bind('<<ListboxSelect>>',preview_unit_list)
        gs.bind('<Return>',start_unit_select)

        def end_init(*args):
            ok_button.unbind('<Return>')
            ok_button['command']=lambda: None
            self.ib['text']=''
            for child in self.root.winfo_children():
                if type(child) == Menu:
                    continue
                for grandkid in child.winfo_children():
                    if type(grandkid) == Listbox:
                        child.destroy()
                        break
                    if len(grandkid.winfo_children()) > 0:
                        for descendent in grandkid.winfo_children():
                            descendent.destroy()
                        break
            self.final_init()

        ok_frame=Frame(self.root,**self.padding)
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

    def stat_preview(self,nergal,frame):

        def show_stats(*args):
            display_cls=self.display_params['Class']
            display_lv=self.display_params['Level']
            stat_labels=stat_names(self.unit_params['game'])
            stat_values=nergal().my_stats
            self.label_array(frame,stat_labels,stat_values,display_cls,display_lv)

        return show_stats


    def get_child_info(self):
        for child in self.root.winfo_children():
            print()
            x=type(child)
            y=child.winfo_geometry()
            z=len(child.winfo_children())
            print(x,y,z)
            for grandkid in child.winfo_children():
                t=type(grandkid)
                g=grandkid.winfo_geometry()
                l=len(grandkid.winfo_children())
                print(t,g,l)

    def final_init(self):
        if not self.game_unit_check():
            return

        fkw={}
        fkw['height']=133
        fkw['width']=196
        fkw.update(self.padding)
        fill_frame=Frame(self.root,**fkw)
        fill_frame.grid(row=0,column=0,sticky=N+S+E+W)

        akw={}
        akw['width']=196
        akw['height']=389
        akw.update(self.padding)
        attr_frame=Frame(self.root,**akw)
        attr_frame.grid(row=1,column=0,sticky=N+S+E+W,rowspan=2)

        #   Inside attr_frame

        attr_label=Label(attr_frame,text='Default')
        underline_font(attr_label)
        attr_label.grid(row=0,sticky=W+N)

        Label(attr_frame,text='').grid(row=1)
        Label(attr_frame,text='').grid(row=2)

        nums_frame=Frame(attr_frame)
        nums_frame.grid(row=3,sticky=W+N+S+E)

        get_default=lambda : Morph(**self.unit_params)
        show_default=self.stat_preview(get_default,nums_frame)

        show_default()

        #   Testing

        l=fill_frame,attr_frame,self.cb
        n='fill','attr','cfg'
        
        for m,name in zip(l,n):
            d=m.grid_info()
            s=m.config()
            row=d['row']
            column=d['column']
            message='Name: %s, Row: %d, Column: %d'%(name,row,column)
            print(s)

        #   Create function that specifies attributes and calls 'show_stats'

        #   has_hm_bonus(**d),\         Checkbutton/Listbox
        #   has_auto_bonus(**d),\       Checkbutton/Listbox
        #   is_lyndis_league(**d),\     Checkbutton
        #   is_fe4_child(**d),\         Listbox = (self.father_select)
        #   is_hugh(**d)                Entry


    def __call__(self):
        self.load_menu()
        self.game_unit_init()
        self.root.mainloop()

if __name__ == '__main__':
    x=Aenir()
    x()
