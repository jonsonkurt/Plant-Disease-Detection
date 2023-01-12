from datetime import datetime
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen
from kivy.lang.builder import Builder
from libs.baseclass import homescreen
from kivymd.uix.pickers import MDTimePicker

# import pyfirmata
# from pyfirmata import Arduino, util
# import time

Builder.load_file('./libs/kv/navigation_layout.kv')

class NavLayoutScreen(Screen):

    # def trial(self):
    #     # Connect to the Arduino board
    #     board = Arduino('/dev/ttyACM0')
    #     it = util.Iterator(board)
    #     it.start()

    #     # Define the LED pin
    #     led_pin = board.get_pin('d:13:o')

    #     # Turn the LED on
    #     led_pin.write(1)
    #     time.sleep(5)

    #     # Turn the LED off
    #     led_pin.write(0)

    #     # Close the connection to the board
    #     board.exit() 
 
    def plant_capture_timer(self):
        time_dialog = MDTimePicker()
        time_dialog.set_time(datetime.now().time())
        time_dialog.bind(on_save=self.save_time, on_cancel=self.cancel_time)
        time_dialog.title = "SET CAPTURING TIME"
        time_dialog.open()

    def save_time(self, instance, time):
        print('Picked time is', time)

    def cancel_time(self, instance, time):
        pass

    def set_time(self, instance, time):
        self.capture_time = time
        print(self.capture_time)
