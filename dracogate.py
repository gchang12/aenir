from aenir2.gui_tools import *
from aenir2.gui_content import *
from aenir2.quintessence import Morph

class Aenir:
    def __init__(self):
        #   Parameters to initalize Morph here
        self.unit_params={}
        self.hm_params={}
        self.auto_params={}
        self.my_unit=None

        #   Parameter for displaying info on-screen
        self.display_params={}

        #   To loop over and generate self.my_unit
        self.init_variables=self.unit_params,\
                             self.hm_params,\
                             self.auto_params

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

        #   To handle various events during initialization

        self.dummy=dummy_message
        self.kishuna=None
        self.initialized=False

    def load_menu(self):
        #   Set root window and frames here
        self.root=Tk()
        self.root.title('Aenir')
        self.root.wm_resizable(width=False,height=False)

        my_width=459

        x=int(self.root.winfo_screenwidth()-my_width)
        y=0
        new_geometry='450x640+%d+%d'%(x,y)
        geometry=self.root.wm_geometry(new_geometry)

        #   Create menus here

        menubar=Menu(self.root,tearoff=0)

        s={'state':DISABLED}

        mainmenu=Menu(menubar,tearoff=0)
        mainmenu.add_command(label='Restart',command=self.restart,accelerator='F5')
        mainmenu.add_command(label='Quit',command=self.quit,accelerator='Esc')

        actionmenu=Menu(menubar,tearoff=0)
        actionmenu.add_command(label='Level Up',accelerator='Ctrl+L')
        actionmenu.add_command(label='Promote',accelerator='Ctrl+P')
        actionmenu.add_command(label='Use Item',accelerator='Ctrl+I')

        viewmenu=Menu(menubar,tearoff=0)
        #   ***Not high priority
        #viewmenu.add_command(label='Session Log')
        viewmenu.add_command(label='Comparison',accelerator='Ctrl+C')

        #   Append menus here

        menubar.add_cascade(label='Main',menu=mainmenu)
        menubar.add_cascade(label='Modify',menu=actionmenu,state=DISABLED)
        menubar.add_cascade(label='View',menu=viewmenu,state=DISABLED)

        self.root.config(menu=menubar)

        #   Create bindings to quit and reset

        self.root.protocol('WM_DELETE_WINDOW',self.quit)
        self.root.bind_all('<Escape>',self.quit)
        self.root.bind_all('<F5>',self.restart)

    def quit(self,*args):
        for var in self.init_variables:
            var.clear()
        self.dummy=dummy_message
        self.my_unit=None
        self.initialized=False
        self.display_params.clear()
        self.root.destroy()

    def restart(self,*args):
        self.quit()
        self.__call__()

    def game_select(self):
        master=self.swFrame1
        itemlist=tuple(game_title_dict().keys())
        height=len(itemlist)+1
        args={'master':master,\
              'itemlist':itemlist,\
              'height':height,\
              'add_scrollbar':True
              }
        self.gsListbox=select_from_list(**args)
        self.gsListbox.bind('<Return>',self.confirm_game)
        self.gsListbox.focus_force()
        self.gsListbox.select_set(0)
        append_listbox_shortcuts(self.gsListbox,self.unit_preview)

    def unit_preview(self,*args):
        anakin(self.seFrame)
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

        self.display_params['Game']='FE'+game
        self.unit_params['game']=game
        self.update_config()

        self.display_params['Title']=title
        self.update_config()

        self.infoLabel['text']='Please select a unit from FE%s.'%game
        self.infoLabel['text']+=self.dummy

    def unit_select(self,game='4'):
        master=self.seFrame
        itemlist=unit_list(game)
        height=28
        args={'master':master,\
              'itemlist':itemlist,\
              'height':height,\
              'add_scrollbar':True
              }
        self.usListbox=select_from_list(**args)
        self.usListbox['state']=DISABLED
        self.usListbox.bind('<Return>',self.confirm_unit)
        kw={
            'val_call':self.usListbox.selection_get,\
            'val_name':'Unit Select',\
            'frame':self.swFrame2
            }
        append_listbox_shortcuts(self.usListbox)

    def disableHM(self):        
        for widget in self.dummy[:-2]:
            cfg={'state':DISABLED}
            widget.config(cfg)

    def chapter_select(self,*args):
        d=self.unit_params
        if d['unit'] == 'Gonzales':
            itemdict=auto_chapter_dict(**d)
            master=self.seFrame1
            self.disableHM()
            val_name='Auto Select'
        elif not has_auto_bonus(**d):
            itemdict=hm_chapter_dict(**d)
            master=self.seFrame1
            self.disableHM()
            val_name='HM Select'
        else:
            itemdict=auto_chapter_dict(**d)
            master=self.swFrame1
            val_name='Auto Select'
        itemlist=tuple(itemdict.keys())
        args=(master,val_name,itemlist)
        self.optionListbox(*args)

    def previewFromListbox(self,*args):
        settings=self.dummy[-3:]
        settings[0].config({'state':NORMAL})
        s={
            'val_name':settings[2],\
            'launch_menu':False,\
            'val_call':settings[1].selection_get
            }
        self.append_bonus(**s)
        self.create_morph()
        self.stat_preview()

    def optionListbox(self,master,val_name,itemlist):
        height=4
        add_scrollbar=True
        width=28
        args={
            'master':master,\
            'itemlist':itemlist,\
            'height':height,\
            'width':width,
            'add_scrollbar':add_scrollbar
            }
        chapterListbox=select_from_list(**args)
        chapterListbox.focus()
        kw={
            'val_name':val_name,\
            'val_call':chapterListbox.selection_get
            }
        g=lambda *args:self.append_bonus(**kw)
        confirmButton=wideButton(master,'Confirm',g,1,state=DISABLED)
        chapterListbox.bind('<<ListboxSelect>>',self.previewFromListbox)
        t=confirmButton,chapterListbox,val_name
        if type(self.dummy) == tuple:
            self.dummy+=t
        else:
            self.dummy=t
        return chapterListbox

    def append_bonus(self,val_name,launch_menu=True,val_call=None):
        other_word='Difficulty'
        if callable(val_call):
            val=val_call()
        if val_name == 'Hard Mode':
            d=self.hm_params
            t={'chapter':''}
            s={'Difficulty':'Hard Mode'}
        elif val_name == 'HM Select':
            d=self.hm_params
            val=hm_chapter_dict(**self.unit_params)[val]
            t={'chapter':val}
            if not launch_menu:
                if other_word not in self.display_params.keys():
                    s={other_word:'Hard Mode'}
                    self.display_params.update(s)
                    self.update_config()
            s={'Chapter':val}
        elif val_name == 'Auto Select':
            d=self.auto_params
            val=auto_chapter_dict(**self.unit_params)[val]
            t={'chapter':val}
            s={'Chapter':val}
        elif val_name == 'Lyn Mode':
            d=self.unit_params
            t={'lyn_mode':val}
            s={'Campaign':('Lyn\'s Story' if val else 'Main Story')}
        elif val_name == 'Father':
            d=self.unit_params
            old_name=get_old_name(d['game'],val)
            t={'father':old_name}
            s={'Father':val}
        elif val_name == 'Gold Given':
            d=self.auto_params
            s={val_name:val}
            num_times=decline_hugh_dict()[val]
            t={'num_times':num_times}
        d.update(t)
        if launch_menu:
            self.display_params.update(s)
            self.update_config()
            if self.unit_params['unit'] == 'Gonzales':
                d=self.hm_params
                word='chapter'
                if word in d.keys():
                    s={other_word:'Hard Mode'}
                    self.display_params.update(s)
                    self.update_config()
            self.launch_main_menu()

    def hm_bonus_select(self):
        d=self.unit_params
        hm_chapters=hard_mode_dict()[d['unit']]
        master=self.swFrame1

        difficulty=BooleanVar()

        btn={
            'row':3,\
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
            'command':self.radiobuttonNM,\
            'variable':difficulty,\
            'value':False,\
            'justify':LEFT
            }

        select_nm=Radiobutton(**nm)

        if has_auto_bonus(**d) or '' not in hm_chapters.keys():
            if not has_auto_bonus(**d):
                command=self.chapter_select
            else:
                command=self.boolHM
                nmCommand['command']=self.chapter_select
                nmCommand['text']='Continue'
            text='Continue'
        else:
            command=self.boolHM
            text='Confirm'

        text_cmd={
            'text':text,\
            'command':command
            }

        hmCommand={'button':advButton}
        hmCommand.update(text_cmd)

        hm={
            'master':master,\
            'text':'Hard',\
            'command':self.radiobuttonHM,\
            'variable':difficulty,\
            'value':True
            }

        select_hm=Radiobutton(**hm)

        g={'sticky':W}

        select_nm.grid(row=0,**g)
        select_hm.grid(row=1,**g)
        Label(master,text='').grid(row=2)

        select_nm.focus()

        self.dummy=(select_nm,select_hm,advButton,hmCommand,nmCommand)

    def radiobuttonNM(self,*args):
        updateButton(**self.dummy[4])
        k=self.display_params
        self.hm_params.clear()
        self.create_morph()
        self.stat_preview()

    def radiobuttonHM(self,*args):
        updateButton(**self.dummy[3])
        d=self.unit_params
        k=self.display_params
        hm_chapters=hard_mode_dict()[d['unit']]
        if '' in hm_chapters.keys():
            val_name='Hard Mode'
            s={
                'launch_menu':False,\
                'val_name':val_name,\
                }
            self.append_bonus(**s)
            self.create_morph()
            self.stat_preview()

    def boolHM(self,*args):
        ab={'val_name':'Hard Mode'}
        d=self.unit_params
        if has_auto_bonus(**d):
            ab.update({'launch_menu':False})
            self.chapter_select()
        self.append_bonus(**ab)

    def boolLM(self,*args):
        kw={
            'val_name':'Lyn Mode',\
            'val_call':self.dummy[0].get
            }
        f=lambda *args: self.append_bonus(**kw)
        kw2=kw.copy()
        kw2['launch_menu']=False
        self.append_bonus(**kw2)
        self.create_morph()
        self.stat_preview()
        wargs=(self.dummy[1],'Confirm',f)
        updateButton(*wargs)

    def campaign_select(self):
        #   *** Must fix Radiobutton auto-fill issue here...
        #   -   Something to do with campaign Variable?
        #   -   Last time, dependent on if handler was method vs. function
        master=self.swFrame1
        campaign=BooleanVar()
        #campaign=StringVar()

        btn={
            'row':3,\
            'master':master,\
            'state':DISABLED,\
            'text':'Confirm',\
            'command':lambda *args: None
            }
        okButton=wideButton(**btn)
        
        lyn={
            'master':master,\
            'text':'Lyn Mode',\
            'command':self.boolLM,\
            'value':True,\
            'variable':campaign
            }
        #lyn['value']=str(lyn['value'])
        chooseLyn=Radiobutton(**lyn)

        eh={
            'master':master,\
            'text':'Eliwood/Hector Mode',\
            'command':self.boolLM,\
            'value':False,\
            'variable':campaign
            }
        #eh['value']=str(eh['value'])
        chooseMain=Radiobutton(**eh)
        self.dummy=(campaign,okButton,chooseLyn,chooseMain)

        g={'sticky':W}

        chooseLyn.grid(row=0,**g)
        chooseMain.grid(row=1,**g)
        Label(master,text='').grid(row=2)

        chooseLyn.focus()
        chooseMain.deselect()
        
    def option_select(self):
        info_text='Some information is missing.\nPlease specify:\n\n'
        d=self.unit_params
        self.seFrame2['text']='Preview'
        self.swFrame2['text']='Default'
        
        swText='Difficulty Mode'
        seText='Recruitment Chapter'
        
        if is_lyndis_league(**d):
            more_text='Campaign'
            self.campaign_select()
        elif is_fe4_child(**d):
            more_text='Father'
            self.father_select()
        elif is_hugh(**d):
            more_text='Amount of Gold Paid'
            self.gold_select()
        elif has_hm_bonus(**d):
            hm_chapters=hard_mode_dict()[d['unit']]
            if has_auto_bonus(**d) or '' not in hm_chapters.keys():
                more_text='\n'.join((swText,seText))
            else:
                more_text=swText
            self.hm_bonus_select()
        elif has_auto_bonus(**d):
            more_text=seText
            self.chapter_select()
        else:
            self.quit()
            
        if '\n' in more_text:
            self.seFrame1['text']=seText
            self.swFrame1['text']=swText
        else:
            self.swFrame1['text']=more_text

        if more_text == 'Father':
            more_text+='\n\n(default father is Arden)'

        return info_text+more_text

    def write_unit_history(self,path):
        frame=self.swFrame1
        y=self.my_unit
        if not frame.winfo_children():
            l1=Label(frame,text='Level')
            l1.grid(row=0,column=0)
            l2=Label(frame,text='Class')
            l2.grid(row=0,column=1)
            underline_font(l1)
            underline_font(l2)
        level=y.current_level()
        minimum_level=y.min_promo_level(path)
        if level < minimum_level:
            level=minimum_level
        level=str(level)
        unit_class=y.current_class()
        row_num=len(frame.winfo_children())/2
        row_num=int(row_num)
        Label(frame,text=level).grid(row=row_num,column=0)
        Label(frame,text=unit_class).grid(row=row_num,column=1)

    def clear_labelframes(self):
        self.seFrame1['text']=' '
        self.seFrame2['text']=' '

    def level_up_menu(self,*args):
        self.clear_mod_frames()
        self.seFrame1['text']='Target Level'
        message=(
            'Please specify the desired level',\
            'for %s.'%self.display_params['Unit'],\
            '',\
            'Press Enter in order to preview stats.'
            )
        self.infoLabel['text']='\n'.join(message)
        master=self.seFrame1
        command1=self.level_up_confirm
        command2=self.launch_main_menu
        okButton,cancelButton=buttonPair(master,command1,command2)
        levels,levelInput=numericalEntry(master)
        levelInput.config({'justify':CENTER,'width':10})
        self.dummy=okButton,levels,levelInput
        levelInput.bind('<Return>',self.level_up_preview)
        self.seFrame2['text']='Preview'
        Label(master,text='').grid(row=0)
        levelInput.grid(row=1,columnspan=2,column=0)
        Label(master,text='').grid(row=2)
        okButton.grid(row=3,column=0)
        cancelButton.grid(row=3,column=1)

    def level_up_confirm(self,*args):
        num_levels=self.fix_level(get_increment=True)
        self.my_unit.level_up(num_levels)
        self.launch_main_menu()

    def level_up_preview(self,*args):
        if not self.dummy[1].get().isdigit():
            return
        message=(
            'Stat preview is in the lower-right.',\
            '',\
            'Press the Confirm button in order',\
            'to apply changes.'
            )
        self.infoLabel['text']='\n'.join(message)
        self.dummy[0].config({'state':NORMAL})
        self.dummy[0].focus()
        self.dummy[1].set(str(self.fix_level()))
        self.dummy[2].config({'state':DISABLED})
        self.kishuna.level_up(self.fix_level(get_increment=True))
        self.stat_preview()
        self.kishuna=self.my_unit.copy()

    def promote_confirm(self,*args):
        if len(self.my_unit.my_promotions) == 1:
            path=0
        else:
            path=self.dummy[3]
        self.write_unit_history(path)
        self.my_unit.promote(path)
        self.launch_main_menu()

    def promote_menu(self,*args):
        self.clear_mod_frames()
        master=self.seFrame1
        promo_to_index={val:key for key,val in self.my_unit.my_promotions.items()}
        promo_list=tuple(promo_to_index.keys())
        command1=self.promote_confirm
        command2=self.launch_main_menu
        text1='Yes'
        text2='No'
        bkw={
            'master':master,\
            'command1':command1,\
            'command2':command2,\
            'text1':text1,\
            'text2':text2
            }
        b1,b2=buttonPair(**bkw)
        if len(promo_to_index) == 1:
            title='Promotion'
            promo_class=promo_list[0]
            message='%s will be promoted to:\n\n%s\n'%(self.display_params['Unit'],promo_class)
            Label(master,text=message).grid(row=0,columnspan=2)
            b1.config({'state':NORMAL})
            b1.focus()
            self.kishuna=self.my_unit.copy()
            self.kishuna.promote()
            self.stat_preview()
            action='confirm'
        else:
            title='Promotion Select'
            pkw={
                'master':master,\
                'itemlist':promo_list,\
                'height':4,\
                'get_var':True
                }
            promoListbox,promoVar=select_from_list(**pkw)
            promoListbox.grid(row=0,columnspan=2)
            promoListbox.focus()
            b1['text']='Confirm'
            b2['text']='Cancel'
            promoListbox.bind('<<ListboxSelect>>',self.promo_preview)
            self.dummy=[b1,promoListbox,promo_to_index,0]
            action='select'
        message=(
            'Please %s promotion or'%action,\
            'press Cancel to return to the',\
            'main menu.',\
            '',\
            'Units who are not high enough a',\
            'level to promote will be automatically',\
            'leveled-up until such is the case.'
            )
        message='\n'.join(message)
        self.infoLabel['text']=message
        master['text']=title
        self.seFrame2['text']='Preview'

    def promo_preview(self,*args):
        self.dummy[0].config({'state':NORMAL})
        self.kishuna=self.my_unit.copy()
        selected_item=self.dummy[1].selection_get()
        path=self.dummy[2][selected_item]
        self.dummy[3]=path
        if type(path) == int:
            f=self.kishuna.promote
        elif type(path) == str:
            f=self.kishuna.use_stat_booster
            boosters=booster_dict(self.unit_params['game'],True)
            text_list=(selected_item,path,boosters[path])
            message='%s: Boosts %s by %d.'%text_list
            self.infoLabel['text']=message
        f(path)
        self.stat_preview()
        self.kishuna=self.my_unit.copy()

    def fix_level(self,get_increment=False,fixed=False):
        num_levels=int(self.dummy[1].get())
        y=self.my_unit
        flag=False
        if num_levels > y.max_level():
            num_levels=y.max_level()
            flag=True
        elif num_levels < y.current_level():
            num_levels=y.current_level()
            flag=True
        if fixed:
            return flag
        if get_increment:
            x=num_levels-y.current_level()
        else:
            x=num_levels
        return x

    def item_menu(self,*args):
        master=self.seFrame1
        self.clear_mod_frames()
        self.seFrame2['text']='Preview'
        kw={
            'game':self.unit_params['game'],\
            'get_bonus':False
            }
        itemlist=booster_dict(**kw)
        item_to_stat={val:key for key,val in itemlist.items()}
        height=5
        gw={
            'master':master,\
            'itemlist':tuple(itemlist.values()),\
            'height':5,\
            'add_scrollbar':True,\
            'get_var':True,\
            'scroll_col':2
            }
        itemListbox,itemVar=select_from_list(**gw)
        itemListbox.grid(row=0,columnspan=2)
        itemListbox.focus()
        itemListbox.bind('<<ListboxSelect>>',self.promo_preview)
        bw={
            'master':master,\
            'command1':self.item_confirm,\
            'command2':self.launch_main_menu,\
            }
        b1,b2=buttonPair(**bw)
        self.dummy=[b1,itemListbox,item_to_stat,'HP']
        title='Stat Booster'
        self.seFrame1['text']=title
        message=(
            'Please select a stat booster',\
            'to use on %s.'%self.display_params['Unit']
            )
        self.infoLabel['text']='\n'.join(message)

    def item_confirm(self,*args):
        self.my_unit.use_stat_booster(self.dummy[3])
        self.launch_main_menu()

    def launch_main_menu(self,*args):
        self.root.unbind('<Key>')
        if not self.initialized:
            self.create_morph(make_dummy=False)
        y=self.my_unit

        frames_to_clear=self.swFrame1,self.swFrame2,self.seFrame1,self.seFrame2
        new_labels='Unit History','Current Stats',' ',' '

        for frame,text in zip(frames_to_clear,new_labels):
            s={'text':text}
            frame.config(s)
            if text == 'Unit History':
                contents=frame.winfo_children()
                labels=[]
                for content in contents:
                    if type(content) == Label:
                        labels+=[content]
                if labels == contents:
                    continue
            anakin(frame)

        self.clear_stats()
        self.insert_stats(show_capped=True)
        self.infoLabel['text']='Welcome to the Main Menu!'

        self.dummy=()

        for widget in self.root.winfo_children():
            if type(widget) != Menu:
                continue
            widget.entryconfig('Modify',state=NORMAL)
            widget.entryconfig('View',state=NORMAL)
            self.dummy+=(widget,)
            for submenu in widget.winfo_children():
                self.dummy+=(submenu,)

        s={'state':DISABLED}

        editmenu=self.dummy[2]

        m1={
            'key':'<Control-l>',\
            'index':'Level Up',\
            'command':self.level_up_menu,\
            'condition':y.current_level() == y.max_level()
            }

        m2={
            'key':'<Control-p>',\
            'index':'Promote',\
            'command':self.promote_menu,\
            'condition':not y.can_promote()
            }

        m3={
            'key':'<Control-i>',\
            'index':'Use Item',\
            'command':self.item_menu,\
            'condition':self.unit_params['game'] == '4'
            }

        self.map_shortcut_keys(**m1)
        self.map_shortcut_keys(**m2)
        self.map_shortcut_keys(**m3)

        viewmenu=self.dummy[3]

        viewmenu.entryconfig('Comparison',command=self.compare_stats)
        self.root.bind_all('<Control-c>',self.compare_stats)

        self.kishuna=self.my_unit.copy()

        self.initialized=True

    def clear_mod_frames(self):
        anakin(self.seFrame1)
        anakin(self.seFrame2)
        self.clear_labelframes()

    def compare_stats(self,*args):
        self.clear_mod_frames()
        master=self.seFrame2
        stat_names=get_stat_names(self.unit_params['game'])
        stat_names=stat_names
        stat_values=tuple(self.my_unit.my_stats)
        self.dummy=()

        Label(master,text='').grid(row=0,column=0)
        Label(master,text='avg').grid(row=0,column=3)
        Label(master,text='').grid(row=0,column=2)
        Label(master,text='user').grid(row=0,column=1)
        Label(master,text='').grid(row=0,column=4)

        w={'width':5,'justify':CENTER}

        for n,(name,value,other_stat) in enumerate(zip(stat_names,stat_values,self.my_unit.growth_rates),start=1):
            if other_stat == 0:
                continue
            value=float(value)
            value=round(value,2)
            value=str(value)
            Label(master,text=name).grid(row=n,column=0)
            Label(master,text=value).grid(row=n,column=3)
            num_ent=numericalEntry(master)
            num_ent[1].bind('<Return>',self.show_comparison)
            num_ent[1].config(w)
            Label(master,text=' - ').grid(row=n,column=2)
            num_ent[1].grid(row=n,column=1,columnspan=1)
            Label(master,text=' = ').grid(row=n,column=4)
            self.dummy+=(num_ent,)

        widget_list=tuple(y for x,y in self.dummy)
        self.seFrame2['text']='Comparison'
        self.infoLabel['text']='Please input your stats here and\npress Enter to show comparison.'

        for n in range(len(widget_list)):
            wid=widget_list[n]
            def make_lambda(x):
                return lambda *args: widget_list[x].focus()            
            if n > 0:
                wid.bind('<Up>', make_lambda(n-1))
                wid.bind('<Prior>', make_lambda(0))
            if n < len(widget_list)-1:
                wid.bind('<Down>', make_lambda(n+1))
                wid.bind('<Next>', make_lambda(-1))
            else:
                break
            wid.bind('<Return>',make_lambda(n+1),add=True)

    def show_comparison(self,*args):
        master=self.seFrame2
        for x,y in self.dummy:
            if not x.get().isdigit():
                return
        user_stats=()
        for x,y in self.dummy:
            y.config({'state':DISABLED})
            stat=int(x.get())
            user_stats+=(stat,)

        Label(master,text='diff').grid(row=0,column=5)
        csum=0

        for n,(mystat,avgstat) in enumerate(zip(user_stats,self.my_unit.my_stats),start=1):
            diff=mystat-float(avgstat)
            diff=round(diff,2)
            csum+=diff
            color=('cyan4' if diff >= 0 else 'red')
            diff=str(diff)
            Label(master,text='').grid(row=n,column=5)
            Label(master,text=diff,foreground=color).grid(row=n,column=5)

        self.seFrame1['text']='Analysis'
        csum=round(csum,2)
        unit_name=self.display_params['Unit']
        adj=('above' if csum >= 0 else 'below')
        message='Your %s is %s average by:\n\n%g points'%(unit_name,adj,csum)
        Label(self.seFrame1,text=message).grid()
        self.infoLabel['text']='Press any key to return to\nthe main menu.'
        self.root.bind('<Key>',self.launch_main_menu)

    def map_shortcut_keys(self,key,index,command,condition):
        editmenu=self.dummy[2]

        if condition:
            s={'state':DISABLED}
            self.root.unbind_all(key)
        else:
            s={'command':command,'state':NORMAL}
            self.root.bind_all(key,command)

        editmenu.entryconfig(index=index,**s)

    def confirm_unit(self,*args):
        self.usListbox.unbind('<Return>')
        self.usListbox['state']=DISABLED

        new_name=self.usListbox.selection_get()
        old_name=get_old_name(self.unit_params['game'],new_name)

        self.display_params['Unit']=new_name
        self.unit_params['unit']=old_name

        self.create_morph(make_dummy=False)

        self.update_config()

        self.seFrame['text']=''

        anakin(self.swFrame1)
        self.seFrame.destroy()
        self.seFrame1=set_mainframe(3,1,self.rWidth,self.dHeight1)
        self.seFrame2=set_mainframe(4,1,self.rWidth,self.dHeight2)

        if not self.game_unit_check():
            message=(
                'Use any of these shortcut keys at',\
                'any time during the session:',\
                '',\
                'F5: Restart session',\
                'Esc: Quit session'
                )
            info_text='\n'.join(message)
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

    def create_morph(self,make_dummy=True):
        if make_dummy:
            self.kishuna=Morph(**self.unit_params)
            y=self.kishuna
        else:
            self.my_unit=Morph(**self.unit_params)
            y=self.my_unit
        if self.hm_params:
            y.add_hm_bonus(**self.hm_params)
        if self.auto_params:
            if self.unit_params['unit'] == 'Hugh':
                f=y.decline_hugh
            else:
                f=y.add_auto_bonus
            f(**self.auto_params)

    def clear_stats(self):
        keys='','Class','Level'
        keys+=get_stat_names(self.unit_params['game'])

        for key in keys:
            self.display_params.pop(key)

    def stat_preview(self):
        assert type(self.my_unit) == type(self.kishuna)
        frame=self.seFrame2
        anakin(self.seFrame2)
        kw_list=[]
        comparison=self.my_unit < self.kishuna
        for val in comparison.values():
            if val is None:
                color=None
            elif val:
                color='cyan4'
            else:
                color='red'
            kw_list+=[{'color':color}]
        kw={
            'frame':self.seFrame2,\
            'y':self.kishuna,\
            'kw_list':kw_list
            }

        self.clear_stats()

        self.show_stat_array(**kw)

    def insert_stats(self,show_capped=False):
        frame=self.swFrame2
        if self.my_unit is None:
            y=Morph(**self.unit_params)
        else:
            y=self.my_unit

        color_cfg={'color':None}
        kw_list=[]

        while len(kw_list) < 2:
            kw_list+=[color_cfg]

        if not show_capped:
            kw_list+=[color_cfg for stat in y.my_stats]
        else:
            comparison=self.my_unit.is_capped()
            for val in comparison.values():
                if not val:
                    color=None
                else:
                    color='green3'
                kw_list+=[{'color':color}]

        self.show_stat_array(frame,y,kw_list)

    def show_stat_array(self,frame,y,kw_list):
        assert len(kw_list) == len(y.my_stats) + 2
        stat_names=get_stat_names(self.unit_params['game'])

        show_stat_pair=lambda **kw:self.update_config(frame=frame,**kw)

        self.display_params['Class']=y.current_class()
        show_stat_pair(**kw_list[0])
        self.display_params['Level']=str(y.current_level())
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

        if label:
            label+=':'

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

    def father_select(self):
        master=self.swFrame1
        itemlist=fe4_father_list()
        add_scrollbar=True
        val_name='Father'
        kwargs={
            'master':master,\
            'val_name':val_name,\
            'itemlist':itemlist
            }
        self.optionListbox(**kwargs)

    def gold_select(self):
        master=self.swFrame1
        itemlist=decline_hugh_dict().keys()
        itemlist=tuple(itemlist)
        val_name='Gold Given'

        kwargs={
            'master':master,\
            'val_name':val_name,\
            'itemlist':itemlist
            }
        self.optionListbox(**kwargs)

    def __call__(self):
        self.load_menu()

        dy=120

        lWidth=200
        rWidth=210

        uHeight=140
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
        text='Please select a game.'+self.dummy
        self.infoLabel=Label(self.neFrame,text=text,justify=LEFT)
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
