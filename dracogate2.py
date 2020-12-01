from aenir2.gui_tools import *
from aenir2.gui_content import *
from aenir2.quintessence import Morph
from aenir2.entry_validator import not_my_validator

class Aenir:
    def __init__(self):
        #   Parameters to initalize Morph here
        self.unit_params={}
        self.hm_params={}
        self.auto_params={}
        self.my_unit=None
        self.session_history={}

        #   Parameter for displaying info on-screen
        self.display_params={}

        #   To clear all variables
        self.info_variables=self.unit_params,\
                             self.hm_params,\
                             self.auto_params,\
                             self.display_params,\
                             self.session_history

        #   GUI variables to be set later
        self.root=None

        self.nwFrame=None

        self.neFrame=None
        self.infoLabel=None

        self.swFrame1=None
        self.gsListbox=None

        self.swFrame2=None

        self.seFrame=None
        self.usListbox=None

        self.seFrame1=None
        self.seFrame2=None

        #   Lengths

        self.dHeight1=0
        self.dHeight2=0
        self.rWidth=0

    def load_menu(self):
        #   Set root window and frames here
        self.root=Tk()
        self.root.title('Aenir')
        self.root.wm_resizable(width=False,height=False)

        my_width=450
        my_width+=9

        x=int(self.root.winfo_screenwidth()-my_width)
        y=0
        new_geometry='450x620+%d+%d'%(x,y)
        geometry=self.root.wm_geometry(new_geometry)

        #   Create menus here

        menubar=Menu(self.root,tearoff=0)

        menubar.add_command(label='Restart',command=self.restart)

        actionmenu=Menu(menubar,tearoff=0)
        actionmenu.add_command(label='Level Up')
        actionmenu.add_command(label='Promote')
        actionmenu.add_command(label='Use Item')

        viewmenu=Menu(menubar,tearoff=0)
        viewmenu.add_command(label='Session Log')
        viewmenu.add_command(label='Comparison')

        #   Append menus here

        menubar.add_cascade(label='Edit',menu=actionmenu,state=DISABLED)
        menubar.add_cascade(label='View',menu=viewmenu,state=DISABLED)

        self.root.config(menu=menubar)

        #   Create bindings to quit and reset

        self.root.protocol('WM_DELETE_WINDOW',self.quit)
        self.root.bind_all('<Escape>',self.quit)
        self.root.bind_all('<F5>',self.restart)

    def quit(self,*args):
        for var in self.info_variables:
            var.clear()
        self.my_unit=None
        self.root.destroy()

    def restart(self,*args):
        self.quit()
        self.__call__()

    def game_select(self):
        master=self.swFrame1
        itemlist=tuple(game_title_dict().keys())
        height=len(itemlist)+1
        args=master,itemlist,height
        self.gsListbox=select_from_list(*args)
        self.gsListbox.bind('<Return>',self.confirm_game)
        self.gsListbox.focus_force()
        self.gsListbox.select_set(0)
        append_listbox_shortcuts(self.gsListbox,self.unit_preview)

    def unit_preview(self,*args):
        title=self.gsListbox.selection_get()
        game=game_title_dict()[title]
        self.unit_select(game)

    def confirm_game(self,*args):
        self.gsListbox.unbind('<Return>')
        self.gsListbox.unbind('<<ListboxSelect>>')

        self.gsListbox['state']=DISABLED
        self.usListbox['state']=NORMAL

        title=self.gsListbox.selection_get()
        game=game_title_dict()[title]

        self.usListbox.focus()
        self.usListbox.select_set(0)

        self.display_params['Game:']='FE'+game
        self.unit_params['game']=game
        self.update_config()

        self.display_params['Title:']=title
        self.update_config()

        self.infoLabel['text']='Please select a unit from FE%s.'%game

    def unit_select(self,game='4'):
        master=self.seFrame
        itemlist=unit_list(game)
        height=28
        args=master,itemlist,height,True
        self.usListbox=select_from_list(*args)
        self.usListbox['state']=DISABLED
        self.usListbox.bind('<Return>',self.confirm_unit)
        kw={
            'val_call':self.usListbox.selection_get,\
            'val_name':'Unit Select',\
            'frame':self.swFrame2
            }
        append_listbox_shortcuts(self.usListbox)

    def chapter_select(self,*args):
        x='Chapter Select still WIP. Please come back later!'
        print(x)
        print('args:',args)

    def append_bonus(self,val_call,val_name,launch_menu=True):
        val=val_call()
        if val_name == 'Hard Mode':
            d=self.hm_params
            t={'chapter':''}
        d.update(t)
        print('Appended %s bonus:'%val_name,d)
        if launch_menu:
            self.launch_main_menu()

    def hm_bonus_select(self):
        #   Ask if HM with Listbox or Radiobutton; preferably latter
        #       if no:
        #           button text = 'Confirm'
        #           self.launch_main_menu
        #       else:
        #           if multi-chapter or Gonzales:
        #               button text = 'Continue'
        #               self.chapter_select
        #           else:
        #               button text = 'Confirm'
        #               self.launch_main_menu
        d=self.unit_params
        hm_chapters=hard_mode_dict()[d['unit']]
        master=self.swFrame1

        difficulty=StringVar(value='')

        btn={
            'row':2,\
            'master':master,\
            'state':DISABLED,\
            'text':'',\
            'command':lambda *args: None
            }

        advButton=wideButton(**btn)

        nmCommand={
            'button':advButton,\
            'text':'Confirm',\
            'command':self.launch_main_menu
            }

        nm={
            'master':master,\
            'text':'Normal',\
            'command':lambda *args: updateButton(**nmCommand),\
            'variable':difficulty,\
            'value':'Normal'
            }

        select_nm=Radiobutton(**nm)
        
        ab={'val_call':difficulty.get,'val_name':'Hard Mode'}

        if has_auto_bonus(**d) or '' not in hm_chapters.keys():
            #   Use listbox
            ab.update({'launch_menu':False})
            boolHM=lambda *args: self.append_bonus(**ab)
            if not has_auto_bonus(**d):
                command=self.chapter_select
                itemlist=hm_chapter_dict(**d)
            else:
                command=boolHM
                itemlist=auto_chapter_dict(**d)
            text_cmd={
                'text':'Continue',\
                'command':command
                }
        else:
            boolHM=lambda *args: self.append_bonus(**ab)
            text_cmd={
                'text':'Confirm',\
                'command':boolHM
                }

        hmCommand={'button':advButton}
        hmCommand.update(text_cmd)

        hm={
            'master':master,\
            'text':'Hard',\
            'command':lambda *args: updateButton(**hmCommand),\
            'variable':difficulty,\
            'value':'Hard'
            }

        select_hm=Radiobutton(**hm)

        g={'sticky':E+W}
        
        select_nm.grid(row=0,**g)
        select_hm.grid(row=1,**g)
        Label(master,text='').grid(row=2)
        advButton.grid(row=3,**g)

        select_nm.focus()
        
    def option_select(self):
        #   ***Create widgets for each in swFrame:
        #   Radiobutton:            LYN MODE
        #   Listbox:                FE4 KID
        #   Radiobutton:            HUGH
        #   Radiobutton/Listbox:    HARD MODE
        #   Radiobutton/Listbox:    AUTO LEVEL

        #   ***Create stat-preview pane in seFrame2:
        #   -   bound to above methods
        #   -   Create Label in neFrame explaining preview
        info_text='Some information is missing.\nPlease specify:\n\n'
        d=self.unit_params
        self.seFrame2['text']='Preview'
        self.swFrame2['text']='Default'
        
        swText='Difficulty Mode'
        seText='Recruitment Chapter'
        
        if is_lyndis_league(**d):
            more_text='Campaign'
        elif is_fe4_child(**d):
            more_text='Father'
        elif is_hugh(**d):
            more_text='Amount of Gold Paid'
        elif has_hm_bonus(**d):
            hm_chapters=hard_mode_dict()[d['unit']]
            if has_auto_bonus(**d) or '' not in hm_chapters.keys():
                more_text='\n'.join((swText,seText))
            else:
                more_text=swText
            self.hm_bonus_select()
        elif has_auto_bonus(**d):
            more_text=seText
        else:
            self.quit()
            
        if '\n' in more_text:
            self.seFrame1['text']=seText
            self.swFrame1['text']=swText
        else:
            self.swFrame1['text']=more_text
            
        return info_text+more_text

    def launch_main_menu(self,*args):
        print('Ctrl+F: def launch_main_menu')
        print('args:',args)

    def confirm_unit(self,*args):
        self.usListbox.unbind('<Return>')
        self.usListbox['state']=DISABLED

        new_name=self.usListbox.selection_get()
        old_name=get_old_name(self.unit_params['game'],new_name)

        self.display_params['Unit:']=new_name
        self.unit_params['unit']=old_name

        self.update_config()

        self.seFrame['text']=''

        anakin(self.swFrame1)
        self.seFrame.destroy()
        self.seFrame1=set_mainframe(3,1,self.rWidth,self.dHeight1)
        self.seFrame2=set_mainframe(4,1,self.rWidth,self.dHeight2)

        if not self.game_unit_check():
            info_text='Use any of these shortcut keys at\nany time during the session:\n\nF5: Restart session\nEsc: Quit session'
            self.swFrame1['text']='Confirm'
            self.swFrame2['text']='Current Stats'

            notification='\nPlease confirm your selection.\n\n'
            Label(self.swFrame1,text=notification,justify=LEFT).grid(row=0,sticky=E+W)

            okcfg={}
            okcfg['master']=self.swFrame1
            okcfg['text']='OK'
            okcfg['command']=self.launch_main_menu
            okcfg['row']=1
            ok_button=wideButton(**okcfg)
            ok_button.focus()
        else:
            info_text=self.option_select()

        self.infoLabel['text']=info_text
        self.insert_stats()

    def insert_stats(self,kishuna=None,show_capped=False,*args):
        color_cfg={'color':None}
        if kishuna is None:
            frame=self.swFrame2
            y=Morph(**self.unit_params)
            kw_list=[color_cfg for stat in y.my_stats]
        else:
            frame=self.seFrame2
            anakin(self.seFrame2)
            kw_list=[]
            y=kishuna
            if not show_capped:
                comparison=y < self.my_unit
                color1='cyan'
                color2='red'
            else:
                comparison=self.my_unit.is_capped()
                color1='green3'
                color2=None
            for val in comparison.values():
                if val is None:
                    color=None
                elif val:
                    color=color1
                else:
                    color=color2
                kw_list+=[{'color':color}]

        while len(kw_list) < len(y.my_stats)+2:
            kw_list.insert(0,color_cfg)

        game=self.unit_params['game']
        stat_names=get_stat_names(game)

        show_stat_pair=lambda **kw:self.update_config(frame=frame,**kw)

        self.display_params['Class:']=y.current_class()
        show_stat_pair(**kw_list[0])
        self.display_params['Level:']=str(y.current_level())
        show_stat_pair(**kw_list[1])
        self.display_params['']=''
        show_stat_pair()

        for stat,num,kw in zip(stat_names,y.my_stats,kw_list[2:]):
            num=round(num,2)
            self.display_params[stat]=str(num)
            show_stat_pair(**kw)

    def update_config(self,frame=None,color=None):
        display_pairs=list(self.display_params.items())
        label,value=display_pairs[-1]
        row=len(display_pairs)-1

        grid_options1={}
        grid_options1['row']=row
        grid_options2=grid_options1.copy()

        if frame is None:
            frame=self.nwFrame
            grid_options1['sticky']=N+W
            grid_options2['sticky']=N+E

        label_options={}
        label_options['master']=frame
        label_options2=label_options.copy()

        if color is not None:
            label_options2.update({'foreground':color})

        grid_options1['column']=0
        grid_options2['column']=1

        Label(text=label,**label_options).grid(**grid_options1)
        Label(text=value,**label_options2).grid(**grid_options2)

    def game_unit_check(self):
        d=self.unit_params
        conditions=(
            is_lyndis_league(**d),\
            is_fe4_child(**d),\
            is_hugh(**d),\
            has_hm_bonus(**d),\
            has_auto_bonus(**d)
            )
        return any(conditions)

    def __call__(self):
        self.load_menu()

        dy=120

        lWidth=200
        rWidth=210

        uHeight=120
        dHeight=369
        dHeight+=dy

        dHeight1=dHeight/3
        dHeight2=2*dHeight/3

        self.dHeight1=dHeight1
        self.dHeight2=dHeight2
        self.rWidth=rWidth

        assert dHeight1+dHeight2 == dHeight

        self.nwFrame=set_mainframe(1,0,lWidth,uHeight,text='Config')

        self.neFrame=set_mainframe(1,1,rWidth,uHeight,text='Info')
        self.infoLabel=Label(self.neFrame,text='Please select a game.',justify=LEFT)
        self.infoLabel.grid(sticky=N+W)

        self.swFrame1=set_mainframe(3,0,lWidth,dHeight1,text='Game Select')
        self.game_select()

        self.swFrame2=set_mainframe(4,0,lWidth,dHeight2)

        self.seFrame=set_mainframe(3,1,rWidth,dHeight,2,text='Unit Select')
        self.unit_select()

        self.root.mainloop()

if __name__ == '__main__':
    x=Aenir()
    x()
