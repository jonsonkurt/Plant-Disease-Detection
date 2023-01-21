import os
import sqlite3
import cv2
import time
import threading
from kivy.uix.floatlayout import FloatLayout
from kivy.lang.builder import Builder
from kivymd.toast.kivytoast import toast
from kivy.uix.screenmanager import Screen
from datetime import datetime
from kivy.properties import StringProperty, NumericProperty, ListProperty, BooleanProperty
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from pyfirmata import Arduino, util
from yolov5 import detect
# -----------------------------------
from kivymd.uix.card import MDCard
from kivy.clock import Clock
from kivy.utils import get_color_from_hex

Builder.load_file('./libs/kv/homescreen.kv')
        
class HomeScreen(Screen):

    time_date = StringProperty()
    plant_status = StringProperty()
    security_status = StringProperty()
    plant_status_color = NumericProperty()
    security_status_color = NumericProperty()
    motion_detected = StringProperty("Yes")
    color = ListProperty([1, 1, 1, 1])
    color_disease = ListProperty([1, 1, 1, 1])
    is_activated = BooleanProperty(False)
    is_disease = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.i = 0 # index into change color list
        self.j = 0

    def on_kv_post(self, base_widget):
        Clock.schedule_interval(self.update_color, .5)
        Clock.schedule_interval(self.update_color1, .5)

    def update_color(self, dt):
        if self.is_activated == True:
            change_color = ['#BC5448', '#2e593b']
            self.color = get_color_from_hex(change_color[self.i])
            self.i = (self.i + 1) % len(change_color)  # loop through all the colors
        else:
            self.color = get_color_from_hex('#2e593b')
    
    def update_color1(self, dt): 
        #print(self.is_disease)
        if self.is_disease == True:       
            change_color1 = ['#BC5448', '#2e593b']
            self.color_disease = get_color_from_hex(change_color1[self.j])
            self.j = (self.j + 1) % len(change_color1)
        else:
            self.color_disease = get_color_from_hex('#2e593b')

    def on_pre_enter(self):
        self.start_hardware()

    def on_enter(self):
        self.status()
        self.start_cam()
        self.get_pstatus()

    def start_hardware(self):
        t = threading.Thread(target=self.hardware)
        t.start()
        
    def hardware(self):
        # COMMENT OUT THIS IF AN ARDUINO IS CONNECTED
        self.board = Arduino('COM3')
        self.it = util.Iterator(self.board)
        self.it.start()
        # self.laser_sensor = self.board.get_pin('a:0:i')
        # self.buzzer = self.board.get_pin('d:8:o')
        # self.pirPin = self.board.get_pin('a:1:i')
        
        # self.HIGH = True
        # self.LOW = False
        # self.calibrationTime = 30
        # self.pause = 5000
        # self.lockLow = True
        # self.takeLowTime = False
        # self.PIRValue = 0
        # self.number = "09272343635"
        # self._timeout = 0
        # self._buffer = ""
        # self.ldr_val = 0
        # #Add the pins of tripwire, motion sensor, and GSM here
        
        # self.tripwire_activator()
        # Add GSM using this self.gsm_activator()
        
        self.pushbutton = self.board.get_pin('d:8:i')
        self.button_activator()

    def button(self):
        while True:
            self.HIGH = True
            self.prev_button_state = self.pushbutton.read() 
            if self.prev_button_state == self.HIGH:
                self.security_warning()
                time.sleep(2) # Adjust this for longer intrusion alert display
                self.security_warning2()
                
    def button_activator(self):
        t = threading.Thread(target=self.button)
        t.start()

    def gsm(self):
        self.tx.write("AT+CMGF=1")
        time.sleep(1)
        self.tx.write('AT+CMGS=\"' + "09272343635" + '\"\r"')
        time.sleep(1)
        self.tx.write("Motion Detected. There is a potential intruder or disturbance on your farm.")
        time.sleep(1)
        self.tx.write(ascii.ctrl('z'))
        time.sleep(1)
        print("DONE")
        
    def gsm_activator(self):
        t = threading.Thread(target=self.gsm)
        t.start()

    def tripwire_alarm(self):
        #Palitan na lang laman ng method na ito
        while True:
            self.motion_sensor = self.pirPin.read()
            self.ldr_val = self.laser_sensor.read()
            
            if self.ldr_val == None:
                continue
            # get val of ldr
            if self.ldr_val > 0.5:
                #print("Buzzer ringing")
                self.buzzer.write(1)
                #self.laser_message() 
                self.security_warning()
                time.sleep(2) # Adjust this for longer intrusion alert display
                self.security_warning2()
                self.gsm_activator()
            
            else:
                self.buzzer.write(0)
####

            print("MOTION SENSOR:  ", self.motion_sensor)
            if self.motion_sensor == None:
                 continue
            if self.motion_sensor > 0.3:
                self.security_warning()
                time.sleep(2) # Adjust this for longer intrusion alert display
                self.security_warning2()
                if self.lockLow == True:
                     self.PIRValue = 1
                     self.lockLow = False
                     # self.motion_message()
                     time.sleep(1)
                    
            if self.motion_sensor < 0.01:
                
                 if self.takeLowTime == False:
                     self.lowIn = time.perf_counter()
                     self.takeLowTime = False
                
                 if not self.lockLow and time.perf_counter() - self.lowIn > self.pause:
                     self.PIRValue = 0
                     self.lockLow = True
                     time.sleep(.5)
                    
            time.sleep(1)

    def tripwire_activator(self):
        t = threading.Thread(target=self.tripwire_alarm)
        t.start()

    def start_cam(self):
        t = threading.Thread(target=self.cam)
        t.start()
        
    def cam(self):
        self.camera = cv2.VideoCapture(0)
        Clock.schedule_interval(self.update, 1.0/30.0)

    def update(self, dt):
        ret, frame = self.camera.read()
        frame = cv2.rotate(frame, cv2.ROTATE_180)

        if ret:
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(frame.tostring(), colorfmt='bgr', bufferfmt='ubyte')
            self.ids.img.texture = texture
        
        conn = sqlite3.connect("mybase.db")
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS scanning_time(id_num integer PRIMARY KEY, plant_scanning_time VARCHAR(30))")

        # Get the time from the database
        cur.execute("SELECT plant_scanning_time FROM scanning_time ORDER BY id_num DESC LIMIT 1")
        db_time = cur.fetchone()[0]

        # Get the current time
        current_time = datetime.now().strftime("%H:%M:%S")

        # Compare the times
        if db_time == current_time:
            self.capture_plant()
            print('Checking for disease')

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
            self.start_detect2()

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
            cur.execute("SELECT disease_history, time_date FROM plant_status ORDER BY id_num DESC LIMIT 1")
            result = cur.fetchone()
            disease_history = result[0]
            time_date = result[1]
            if disease_history == "DISEASE DETECTED":
                self.is_disease = True
            else:
                self.is_disease = False
            
            self.disease_warning(disease_history, time_date)

    def status(self):
        # Plant Status
        self.plant_status_color = 1
        
        # Security Status
        self.security_status_color = 1

    def disease_warning(self,status,time_date):
        pstatus = status
        date_string = time_date

        # Split the string using "_" as the delimiter
        date_parts = date_string.split("_")

        # Extract the time and date parts
        time_parts = date_parts[0].split("-")
        date_parts = date_parts[1].split("-")

        # Convert the time parts to a string in the format "HH:MM"
        time_string = "{}:{}".format(time_parts[0], time_parts[1])

        # Convert the date parts to a string in the format "YYYY-MM-DD"
        date_string = "{}-{}-{}".format(date_parts[2], date_parts[0], date_parts[1])

        # Convert the date string to a datetime object
        now = datetime.now()
        date_object = now.strptime(date_string, "%Y-%m-%d")

        # Format the date object to the desired string "As of 12:22, January 1, 2023"
        formatted_date = "As of {}, {}".format(time_string, date_object.strftime("%B %d, %Y"))
        
        disease_warning_text = self.ids['plant_text'].text = "[font=Fonts/Roboto-Black]" + pstatus + "[/font]"
        disease_warning_text2 = self.ids['plant_text2'].text = "[font=Fonts/Roboto-MediumItalic]" + formatted_date + "[/font]"
        
        return disease_warning_text, disease_warning_text2

    def security_warning(self):
        self.is_activated = True
        security_warning_text = self.ids['security_text'].text = "[font=Fonts/Roboto-Black]INTRUSION DETECTED[/font]"
        security_warning_text2 = self.ids['security_text2'].text = "[font=Fonts/Roboto-MediumItalic]There is a potential intruder or disturbance on your farm.[/font]"
        return security_warning_text, security_warning_text2

    def security_warning2(self):
        self.is_activated = False
        security_warning_text = self.ids['security_text'].text = "[font=Fonts/Roboto-Black]NO INTRUSION DETECTED[/font]"
        security_warning_text2 = self.ids['security_text2'].text = "[font=Fonts/Roboto-MediumItalic] [/font]"
        return security_warning_text, security_warning_text2

    def on_exit(self):
        self.camera.release()
        self.layout.remove_widget(self.img)
        Clock.unschedule(self.update)
        self.board.exit()