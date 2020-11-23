from tkinter import *
from tkinter import ttk

from aenir2.name_lists import game_title_dict

class Limstella:
    def __init__(self):
        self.unit_parameters={}
        self.hm_parameters={}
        self.auto_parameters={}
        self.misc_parameters={}
        self.info_variables=self.unit_parameters,self.hm_parameters,self.auto_parameters,self.misc_parameters
        self.my_unit=None

    def __del__(self):
        for var in self.info_variables:
            var.clear()
        self.my_unit=None

    def __bool__(self):
        return any(self.info_variables) and self.my_unit is None
