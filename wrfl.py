import RPi.GPIO as GPIO
import time
import os
import picamera
from bottle import route, run, template, redirect, static_file
from shutil import copyfile

# Pin 18 als Ausgang deklarieren
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)

CAMLED = 32
GPIO.setup(CAMLED, GPIO.OUT, initial=False) 

Servo = GPIO.PWM(18, 50)

@route('/')
def index():
    return template('index')

@route('/wrfl')
def index():
	Servo.start(1.55)
	time.sleep(1)
	Servo.start(7)
	with picamera.PiCamera() as camera:
	    camera.resolution = (1024, 768)
	    camera.color_effects = (128, 128)
	    camera.start_preview()
	    camera.crop = (0.55, 0.35, 0.2, 0.2)
	    GPIO.output(CAMLED,False)
	    # Camera warm-up time
	    time.sleep(0.8)
	    camera.capture('img/w.jpg', resize=(80, 60))
	copyfile('img/w.jpg', 'img/foo-'+ str(int(time.time())) + '.jpg')
        redirect('/')

@route('/img/<filename>')
def server_static(filename):
	return static_file(filename, root='./img')	

@route('/css/<filename>')
def server_static(filename):
	return static_file(filename, root='./css')	
run(host='0.0.0.0', port=8080)
