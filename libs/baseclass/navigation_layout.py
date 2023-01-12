from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen
from kivy.lang.builder import Builder
from libs.baseclass import homescreen
from kivymd.uix.pickers import MDTimePicker

Builder.load_file('./libs/kv/navigation_layout.kv')

class NavLayoutScreen(Screen):
 
    def plant_capture_timer(self):
        time_dialog = MDTimePicker()
        time_dialog.open()
        
        # print('Set time')