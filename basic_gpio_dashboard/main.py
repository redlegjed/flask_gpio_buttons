"""
GPIO control server
====================

Present a dashboard of buttons that control the state of selected
GPIO pins

Acknowledgements:
This code was adapted from:
http://mattrichardson.com/Raspberry-Pi-Flask


"""
import os
import RPi.GPIO as GPIO
import csv
from subprocess import check_call
from flask import Flask, render_template, request
app = Flask(__name__)

GPIO.setmode(GPIO.BCM)

basepath = os.path.dirname(__file__)
print(basepath)

# Create a dictionary called pins to store the pin number, 
# name, and pin state:
filename = os.path.join(basepath,'pin_table.csv')

if os.path.exists(filename):
   # Load GPIO pin configuration from file
   pins = {}        
   with open(filename, newline='') as csvfile:
      reader = csv.DictReader(csvfile)
      for row in reader:
         # Read default state
         if row['state'].lower() =='on':
            state = GPIO.HIGH
         else:
            state = GPIO.LOW
            
         pins[int(row['pin'])] = {'name':row['name'], 'state':state}
else:
   # Default pin configuration
   pins = {
      23 : {'name' : 'GPIO23', 'state' : GPIO.LOW},
      24 : {'name' : 'GPIO24', 'state' : GPIO.LOW}
      }


# Set each pin as an output and set the state specifed in pins:
for pin in pins:
   GPIO.setup(pin, GPIO.OUT)
   GPIO.output(pin, pins[pin]['state'])

@app.route("/")
def main():
   # For each pin, read the pin state and store it in the pins dictionary:
   for pin in pins:
      pins[pin]['state'] = GPIO.input(pin)

   # Put the pin dictionary into the template data dictionary:
   templateData = {
      'pins' : pins
      }
   # Pass the template data into the template main.html and return it to the user
   return render_template('main.html', **templateData)


@app.route("/setpin/<changePin>/<action>")
def setpin(changePin, action):
   """
   Set the GPIO pin state

   Parameters
   ----------
   changePin : str
       Pin number as a string from URL
   action : str
       'on', 'off' or 'toggle'

   Returns
   -------
   str
       info message
   """
   
   # Convert the pin from the URL into an integer:
   changePin = int(changePin)
   
   # Get the device name for the pin being changed:
   deviceName = pins[changePin]['name']
   
   # If the action part of the URL is "on," execute the code indented below:
   if action == "on":
      # Set the pin high:
      GPIO.output(changePin, GPIO.HIGH)
      # Save the status message to be passed into the template:
      message = "Turned " + deviceName + " on."
      
   if action == "off":
      GPIO.output(changePin, GPIO.LOW)
      message = "Turned " + deviceName + " off."
      
   if action == "toggle":
      # Read the pin and set it to whatever it isn't (that is, toggle it):
      GPIO.output(changePin, not GPIO.input(changePin))
      message = "Toggled " + deviceName + "."

   print(message) # For debugging
   return message



@app.route("/ping/<pin>")
def ping(pin):
   """
   Test function, for checking communication with server

   Parameters
   ----------
   pin : str
       Pin number as str

   Returns
   -------
   str
       Returns 'pong'
   """
   pin = int(pin)
   print('Pong %i' % pin)
   return 'pong'
   
@app.route("/reboot")
def reboot():
   check_call(['sudo', 'reboot','now'])


if __name__ == "__main__":
   app.run(host='0.0.0.0', port=10000, debug=True)
