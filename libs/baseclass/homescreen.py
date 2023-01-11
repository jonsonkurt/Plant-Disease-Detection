from kivymd.app import MDApp
from kivy.lang.builder import Builder
from kivymd.toast.kivytoast import toast
from kivy.uix.screenmanager import Screen
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivy.properties import StringProperty


Builder.load_file('./libs/kv/homescreen.kv')

class HomeScreen(Screen):

    def on_enter(self):
        pass