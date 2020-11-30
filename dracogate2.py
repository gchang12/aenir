from tkinter import *

from aenir2.gui_tools import *
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
        self.nwLabel=None

        self.neFrame=None
        self.neLabel=None
        self.infoLabel=None

        self.swFrame1=None
        self.swLabel=None
        self.gsListbox=None

        self.swFrame2=None

        self.seFrame=None
        self.seLabel=None
        self.usListbox=None

        self.seFrame1=None
        self.seFrame2=None

        #   Lengths

        self.dHeight1=0
        self.dHeight2=0
        self.rWidth=0

    def set_mainframe_label(self,text,row,column):
        label=Label(self.root,text=text)
        label.grid(sticky=N+W,row=row,column=column)
        return label

    def set_all_labels(self,nw,ne,sw,se):
        self.nwLabel=self.set_mainframe_label(nw,0,0)
        self.neLabel=self.set_mainframe_label(ne,0,1)
        self.swLabel=self.set_mainframe_label(sw,2,0)
        self.seLabel=self.set_mainframe_label(se,2,1)

    def set_mainframe(self,row,column,width,height,rowspan=1):
        kw={
            'padx':4,\
            'pady':4,\
            'borderwidth':2,\
            'width':width,\
            'height':height,\
            'relief':'sunken'
            }
        frame=Frame(self.root,**kw)
        frame.grid_propagate(0)
        grid_kw={
            'padx':0,\
            'pady':0
            }
        frame.grid(row=row,column=column,rowspan=rowspan,**grid_kw)
        return frame

    def load_menu(self):
        #   Set root window and frames here
        self.root=Tk()
        self.root.title('Aenir')
        self.root.wm_resizable(width=False,height=False)

        #   Failed attempt at adjusting window position
        #   -   window dimensions inadvertently set to 1x1
        geometry=self.root.wm_geometry()
        #   str:    widthxheight+x+y
        new_geometry=geometry.split('+')
        #   list:   [widthxheight,x,y]
        x_pos=new_geometry[1]
        y_pos=geometry[2]
        x_pos=2*self.root.winfo_screenwidth()/3
        y_pos=self.root.winfo_screenheight()/3
        new_geometry[1]=str(int(x_pos))
        new_geometry[2]=str(int(y_pos))
        geometry='+'.join(new_geometry)
        #self.root.wm_geometry(geometry)

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

    def select_from_list(self,master,itemlist,height,add_scrollbar=False):
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

    def game_select(self):
        master=self.swFrame1
        itemlist=tuple(game_title_dict().keys())
        height=len(itemlist)+1
        args=master,itemlist,height
        self.gsListbox=self.select_from_list(*args)
        self.gsListbox.bind('<<ListboxSelect>>',self.unit_preview)
        self.gsListbox.bind('<Return>',self.confirm_game)
        self.gsListbox.focus_force()
        self.gsListbox.select_set(0)

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
        self.usListbox=self.select_from_list(*args)
        self.usListbox['state']=DISABLED
        self.usListbox.bind('<Return>',self.confirm_unit)
        keys='<End>','<Home>','<Prior>','<Next>'
        for key in keys:
            self.usListbox.bind(key,self.jump_in_us)

    def jump_in_us(self,*args):
        x=args[0].keysym
        current_index=self.usListbox.curselection()[0]
        height=self.usListbox['height']
        length=self.usListbox.size()-1
        self.usListbox.selection_clear(0,length)
        if x in ('End','Home'):
            if x == 'End':
                target=length
            else:
                target=0
            number=target-current_index
            self.usListbox.yview_scroll(number,'units')
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
            self.usListbox.yview_scroll(number,'units')
        else:
            return
        self.usListbox.select_set(target)


    def anakin(self,frame):
        for child in frame.winfo_children():
            child.destroy()

    def confirm_unit(self,*args):
        #   ***Create OK button in Game Select
        self.usListbox.unbind('<Return>')
        self.usListbox['state']=DISABLED

        new_name=self.usListbox.selection_get()
        old_name=get_old_name(self.unit_params['game'],new_name)

        self.display_params['Unit:']=new_name
        self.unit_params['unit']=old_name

        self.update_config()

        self.seLabel['text']=''

        self.anakin(self.swFrame1)
        self.seFrame.destroy()
        self.seFrame1=self.set_mainframe(3,1,self.rWidth,self.dHeight1)
        self.seFrame2=self.set_mainframe(4,1,self.rWidth,self.dHeight2)

        if not self.game_unit_check():
            info_text='Please confirm your selection.\n\nF5: Restart session\nEsc: Quit session'
            self.swLabel['text']='Confirm'
        else:
            #   ***Create widgets for each in swFrame:
            #   Checkbutton:            LYN MODE
            #   Listbox:                FE4 KID
            #   Entry:                  HUGH
            #   Checkbutton/Listbox:    HARD MODE
            #   Listbox:                AUTO LEVEL

            #   ***Create stat-preview pane in seFrame2:
            #   -   bound above methods
            #   -   Create Label in seFrame1 pointing to seFrame2
            info_text='Some information is missing.\nPlease specify:\n\n'
            d=self.unit_params
            if is_lyndis_league(**d):
                more_text='Lyn Mode'
            elif is_fe4_child(**d):
                more_text='Father'
            elif is_hugh(**d):
                more_text='Number of Declines'
            elif has_hm_bonus(**d) and has_auto_bonus(**d):
                #   ***seFrame1: for Gonzales and his dual configurations
                #   -   not activated until Hard Mode specified
                #   -   Create separate method
                swText='Hard Mode'
                seText='Chapter'
                more_text='\n'.join((swText,seText))
                self.seLabel['text']=seText
                self.swLabel['text']=swText
            elif has_hm_bonus(**d):
                k=hard_mode_dict()[d['unit']]
                if '' in k.keys():
                    more_text='Hard Mode'
                else:
                    more_text='Chapter'
            elif has_auto_bonus(**d):
                more_text='Chapter'
            else:
                self.quit()
            info_text+=more_text
            if self.unit_params['unit'] != 'Gonzales':
                self.swLabel['text']=more_text

        self.infoLabel['text']=info_text
        self.insert_stats()

    def insert_stats(self,kishuna=None,*args):
        if kishuna is None:
            frame=self.swFrame2
            y=Morph(**self.unit_params)
            kw_list=[{'color':None} for stat in y.my_stats]
        else:
            frame=self.seFrame2
            self.anakin(self.seFrame2)
            y=kishuna
            comparison=y > self.my_unit
            kw_list=[]
            for val in comparison.values():
                if val is None:
                    color=None
                elif val:
                    color='cyan'
                else:
                    color='red'
                kw_list+=[{'color':color}]
        game=self.unit_params['game']
        stat_names=get_stat_names(game)

        show_stat_pair=lambda **kw:self.update_config(frame=frame,**kw)

        self.display_params['Class:']=y.current_class()
        show_stat_pair(**kw_list[0])
        self.display_params['Level:']=str(y.current_level())
        show_stat_pair(**kw_list[1])
        self.display_params['']=''
        show_stat_pair()

        if len(kw_list) > len(stat_names):
            kw_list=kw_list[2:]

        for stat,num,kw in zip(stat_names,y.my_stats,kw_list):
            self.display_params[stat]=str(num)
            show_stat_pair(**kw)

    def update_config(self,frame=None,color=None):
        #   ***Must center-justify stats somehow...

        display_pairs=list(self.display_params.items())
        label,value=display_pairs[-1]
        row=len(display_pairs)-1

        grid_options1={}
        grid_options1['row']=row
        grid_options2=grid_options1.copy()

        label_options={}

        if frame is None:
            frame=self.nwFrame
            grid_options1['sticky']=N+W
            grid_options2['sticky']=N+E
        if color is not None:
            grid_options2.update({'foreground':color})

        Label(frame,text=label,**label_options).grid(column=0,**grid_options1)
        Label(frame,text=value,**label_options).grid(column=1,**grid_options2)

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
        self.set_all_labels('Config','Info','Game Select','Unit Select')

        dy=100

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

        self.nwFrame=self.set_mainframe(1,0,lWidth,uHeight)

        self.neFrame=self.set_mainframe(1,1,rWidth,uHeight)
        self.infoLabel=Label(self.neFrame,text='Please select a game.',justify=LEFT)
        self.infoLabel.grid(sticky=N+W)

        self.swFrame1=self.set_mainframe(3,0,lWidth,dHeight1)
        self.game_select()

        self.swFrame2=self.set_mainframe(4,0,lWidth,dHeight2)

        self.seFrame=self.set_mainframe(3,1,rWidth,dHeight,2)
        self.unit_select()

        self.root.mainloop()

if __name__ == '__main__':
    x=Aenir()
    x()
