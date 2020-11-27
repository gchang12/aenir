#   https://stackoverflow.com/questions/4140437/interactively-validating-entry-widget-content-in-tkinter

def not_my_validator(inStr,acttyp):
    '''
    Validation function for Entry widget; allows only non-negative integers.
    :param inStr:
    :param acttyp:
    :return: bool
    '''
    if acttyp == '1':  # insert
        if not inStr.isdigit():
            return False
    return True

if __name__ == '__main__':
    from tkinter import *
    
    root=Tk()

    k=5
    d={}
    d['pady']=k
    d['padx']=k

    entry_frame=Frame(root,**d)
    entry_frame.grid(row=1,column=0)

    num_lv=IntVar()
    
    entry=Entry(entry_frame,textvariable=num_lv,validate='key')
    entry['vcmd']=(entry.register(not_my_validator), '%P', '%d')

    def get_and_print(*args):
        n=entry.get()
        print(n,type(n))
        root.destroy()
        exit()

    entry.bind('<Return>',get_and_print)
    entry.grid()
    entry.focus()

    root.mainloop()
