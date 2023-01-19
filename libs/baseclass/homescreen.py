import os
import sqlite3
from kivymd.app import MDApp
from kivy.lang.builder import Builder
from kivymd.toast.kivytoast import toast
from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog
from datetime import datetime
from kivy.properties import StringProperty, NumericProperty

import cv2
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivymd.uix.screen import MDScreen
from kivy.uix.floatlayout import FloatLayout

from pyfirmata import Arduino, util
import time
import threading
from kivy.graphics import Color

from yolov5 import detect

import schedule

Builder.load_file('./libs/kv/homescreen.kv')

class HomeScreen(Screen):

    time_date = StringProperty()
    plant_status = StringProperty()
    security_status = StringProperty()
    plant_status_color = NumericProperty()
    security_status_color = NumericProperty()

    # def gsm(self):
    #     # Turn the LED on
    #     self.led_pin.write(1)
    #     time.sleep(10)

    #     # Turn the LED off
    #     self.led_pin.write(0)
        
    # def activate_gsm(self):
    #     t = threading.Thread(target=self.gsm)
    #     t.start()

    def security_warning2(self):
        security_warning_text = self.ids['security_text'].text = "[font=Fonts/Roboto-Black]NO INTRUSION DETECTED[/font]"
        security_warning_text2 = self.ids['security_text2'].text = "[font=Fonts/Roboto-MediumItalic]Motion Detected: No     Tripwire Interrupted: No[/font]"
        return security_warning_text, security_warning_text2

    def tripwire_alarm(self):
        while True:
            self.HIGH = True
            self.prev_button_state = self.pushbutton.read() 
            if self.prev_button_state == self.HIGH:
                # self.activate_gsm()
                self.security_warning()
                time.sleep(5) # Adjust this for longer intrusion alert display
                self.security_warning2()
                
    def tripwire_activator(self):
        t = threading.Thread(target=self.tripwire_alarm)
        t.start()

    def disease_warning(self,status):
        pstatus = status
        disease_warning_text = self.ids['plant_text'].text = "[font=Fonts/Roboto-Black]" + pstatus + "[/font]"
        disease_warning_text2 = self.ids['plant_text2'].text = "[font=Fonts/Roboto-MediumItalic]" + self.time_date + "[/font]"
        return disease_warning_text, disease_warning_text2

    def security_warning(self):
        security_warning_text = self.ids['security_text'].text = "[font=Fonts/Roboto-Black]INTRUSION DETECTED[/font]"
        security_warning_text2 = self.ids['security_text2'].text = "[font=Fonts/Roboto-MediumItalic]Motion Detected: No     Tripwire Interrupted: Yes[/font]"
        return security_warning_text, security_warning_text2

    def call_camera(self):
        t = threading.Thread(target=self.capture_plant)
        t.start()

    def check_time(self):
        schedule.every(1).seconds.do(self.check_time_and_scan)

        while True:
            schedule.run_pending()
            time.sleep(1)

    def start_checking_time(self):
        t = threading.Thread(target=self.check_time)
        t.start()

    def get_pstatus(self):
        t = threading.Thread(target=self.listen_to_db_changes)
        t.start()

    def listen_to_db_changes(self):
        conn = sqlite3.connect('mybase.db')
        cur = conn.cursor()
        cur.execute("""
            CREATE TRIGGER IF NOT EXISTS update_label
            AFTER UPDATE ON plant_status 
            BEGIN
                UPDATE label_text SET text = new.disease_history  ;
            END;
        """)
        conn.commit()

        cur.execute("SELECT disease_history FROM plant_status ORDER BY id_num DESC LIMIT 1")
        result = cur.fetchone()[0]

        cur.execute("""
            SELECT name FROM sqlite_master WHERE type='trigger'
        """)
        triggers = cur.fetchall()
        print(triggers)

        while True:
            cur.execute("SELECT disease_history FROM plant_status ORDER BY id_num DESC LIMIT 1")
            result = cur.fetchone()[0]
            self.disease_warning(result)

    def start_cam(self):
        t = threading.Thread(target=self.cam)
        t.start()
        
    def cam(self):
        self.camera = cv2.VideoCapture(0)
        self.img = Image()
        Clock.schedule_interval(self.update, 1.0/30.0)

    def start_hardware(self):
        t = threading.Thread(target=self.hardware)
        t.start()
        
    def hardware(self):
        # COMMENT OUT THIS IF AN ARDUINO IS CONNECTED
        self.board = Arduino('COM3')
        self.it = util.Iterator(self.board)
        self.it.start()
        self.led_pin = self.board.get_pin('d:13:o')
        self.pushbutton = self.board.get_pin('d:8:i')
        
        self.tripwire_activator()

    def on_enter(self):
        self.status()
        self.get_pstatus()

    def on_pre_enter(self):
        self.start_hardware()
        self.start_cam()

    def update(self, dt):
        ret, frame = self.camera.read()
        frame = cv2.rotate(frame, cv2.ROTATE_180)

        if ret:
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(frame.tostring(), colorfmt='bgr', bufferfmt='ubyte')
            self.ids.img.texture = texture
        
        conn = sqlite3.connect("mybase.db")
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS scanning_time(plant_scanning_time VARCHAR(30))")

        # Get the time from the database
        cur.execute("SELECT max(plant_scanning_time) FROM scanning_time")
        db_time = cur.fetchone()[0]

        # Get the current time
        current_time = datetime.now().strftime("%H:%M:%S")

        # Compare the times
        if db_time == current_time:
            self.capture_plant()
            print('Checking for disease')

    def status(self):
        
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

    def capture_plant(self):
        ret, frame = self.camera.read()
        if ret:
            now = datetime.now()
            self.time_date_captured = now.strftime("%H-%M_%m-%d-%Y")
            print(self.time_date_captured)
            self.image_time_date = self.time_date_captured
            file_path = "./yolov5/data/images/plant.jpg"
            file_path2 = "./images/" + self.image_time_date + ".jpg"
            cv2.imwrite(file_path, frame)
            cv2.imwrite(file_path2, frame)
            toast("Image saved!")
            self.start_detect()

    def start_detect2(self):
        detect.run()

    def start_detect(self,):
        t = threading.Thread(target=self.start_detect2)
        t.start()

    def check_disease(self, path):
        folder_path = path
        isExist = os.path.exists(folder_path)
        
        now = datetime.now()
        time_date_captured = now.strftime("%H-%M_%m-%d-%Y")
        pstatus_date = time_date_captured

        conn = sqlite3.connect("mybase.db")
        cur = conn.cursor()
            
        if isExist == True:
            # self.disease_warning()
            dir = os.listdir(folder_path)
            if len(dir) == 0:
                pstatus = "NO DISEASE DETECTED"
                cur.execute("CREATE TABLE IF NOT EXISTS plant_status(id_num integer PRIMARY KEY, disease_history VARCHAR(30), time_date VARCHAR(30))")
                cur.execute("INSERT INTO plant_status(disease_history, time_date) VALUES(?,?)", (pstatus, pstatus_date,))
                cur.execute("SELECT * FROM plant_status")
                conn.commit()
                conn.close()

                print('WALA PONG DISEASE')
            else:
                pstatus = "DISEASE DETECTED"
                
                cur.execute("CREATE TABLE IF NOT EXISTS plant_status(id_num integer PRIMARY KEY, disease_history VARCHAR(30), time_date VARCHAR(30))")
                cur.execute("INSERT INTO plant_status(disease_history, time_date) VALUES(?,?)", (pstatus, pstatus_date,))
                cur.execute("SELECT * FROM plant_status")
                conn.commit()
                conn.close()

                print('MAY DISEASE PO')

    def on_exit(self):
        self.camera.release()
        self.layout.remove_widget(self.img)
        Clock.unschedule(self.update)
        self.board.exit()