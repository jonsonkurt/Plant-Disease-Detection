from kivymd.app import MDApp
from kivy.lang.builder import Builder
from kivymd.toast.kivytoast import toast
from kivy.uix.screenmanager import Screen
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from datetime import datetime
from kivy.properties import StringProperty, NumericProperty

Builder.load_file('./libs/kv/homescreen.kv')

class HomeScreen(Screen):
    
    time_date = StringProperty()
    plant_status = StringProperty()
    security_status = StringProperty()
    plant_status_color = NumericProperty()
    security_status_color = NumericProperty()

    def on_enter(self):
        
        # Date and Time
        now = datetime.now()
        current_time = now.strftime("%I:%M %p")
        current_date = now.strftime("%B %d, %Y")
        self.time_date = "As of " + current_time + ", " + current_date

        # Plant Status
        self.plant_status = "NO DISEASE DETECTED"
        self.plant_status_color = 1
        
        # Security Status
        self.security_status = "NO INTRUSION DETECTED"
        self.security_status_color = 1