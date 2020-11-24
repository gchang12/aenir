from tkinter import *
from tkinter import ttk

from aenir2.name_lists import game_title_dict,character_list

root=Tk()
root.title('Please select a game')
mainframe=ttk.Frame(root)
mainframe.grid()
d=game_title_dict()
lvar=tuple(d.keys())
s=StringVar(value=lvar)
s=lvar
lbox=ttk.Combobox(mainframe,values=s)
lbox.grid(row=0,column=1)
game_lbl=ttk.Label(mainframe,text='Game')
game_lbl.grid(row=0,column=0)
unit_params={}

def bind_func(*args):
    global d
    key=lbox.selection_get()
    unit_params.update({'game':d[key]})
    t=StringVar(value=character_list(**unit_params))
    t=character_list(**unit_params)
    lbox2=ttk.Combobox(mainframe,values=t)
    lbox2.grid(row=1,column=1)
    name_lbl=ttk.Label(mainframe,text='Unit')
    name_lbl.grid(row=1,column=0)
    def bind_func2(*args):
        unit_params.update({'unit':lbox2.selection_get()})
        root.destroy()
    lbox2.bind('<Return>',bind_func2)
    lbox2.focus()

lbox.bind('<Return>',bind_func)
lbox.focus()

def add_button():
    btnkw={
        'text':'Quit',\
        'command':lambda *args: root.destroy()
        }
    button=ttk.Button(mainframe,**btnkw)
    button.grid()

root.mainloop()

print(unit_params)
