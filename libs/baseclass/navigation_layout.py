from datetime import datetime
import sqlite3
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen
from kivy.lang.builder import Builder
from libs.baseclass import homescreen
from kivymd.uix.pickers import MDTimePicker
from kivymd.toast.kivytoast import toast
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivy.uix.boxlayout import BoxLayout

Builder.load_file('./libs/kv/navigation_layout.kv')

class NavLayoutScreen(Screen):

    dialog = None
 
    def plant_capture_timer(self):
        time_dialog = MDTimePicker()
        time_dialog.set_time(datetime.now().time())
        time_dialog.bind(on_save=self.save_time, on_cancel=self.cancel_time)
        time_dialog.title = "SET CAPTURING TIME"
        time_dialog.open()

    def save_time(self, instance, time):
        print('Picked time is', time)
        final_time =  str(time)
        conn = sqlite3.connect("mybase.db")
        cur = conn.cursor()
        
        cur.execute("CREATE TABLE IF NOT EXISTS scanning_time(plant_scanning_time VARCHAR(30))")
        cur.execute("INSERT INTO scanning_time(plant_scanning_time) VALUES(?)", (final_time,))
        cur.execute("SELECT * FROM scanning_time")
        conn.commit()

        toast('Scanning Time Scheduled Successfully.')

        conn.close()

    def cancel_time(self, instance, time):
        pass

    def set_time(self, instance, time):
        self.capture_time = time
        print(self.capture_time)
        
    def add_contact(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title="ADD CONTACT",
                type = "custom",
                content_cls = AddContact(),
            )
        self.dialog.open()

class AddContact(BoxLayout):
    
    def save_contact(self, contact_add):
        final_contact = str(contact_add)
        conn = sqlite3.connect("mybase.db")
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS contacts(phone_number VARCHAR(30))")
        cur.execute("INSERT INTO contacts(phone_number) VALUES(?)", (final_contact,))
        cur.execute("SELECT * FROM contacts")
        conn.commit()
        toast('Contact Added Successfully.')
        conn.close()