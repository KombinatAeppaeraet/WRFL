import RPi.GPIO as GPIO
import time
import os
import picamera
import bottle
from bottle import route, run, template, redirect, static_file
from shutil import copyfile
import wrfl_count
import json
import wrfl_twitter



bottle.TEMPLATE_PATH.insert(0,'/opt/wrfl/views')

# Pin 18 als Ausgang deklarieren
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)

CAMLED = 32
GPIO.setup(CAMLED, GPIO.OUT, initial=False)

Servo = GPIO.PWM(18, 50)


def fileAge(fname):
    # returns age of file in seconds
    st = os.stat(fname)
    age = (time.time() - st.st_mtime)
    return age


def isRolling():
    # checks if a request is active
    if os.path.isfile('rolling'):
        # ignore too old files
        if fileAge('rolling') > 30:
            endRolling()
            return False
        else:
            return True


def startRolling():
    # touches file to indicate an active roll process
    open('rolling', 'a').close()


def endRolling():
    # removes file to indicate and of roll process
    if os.path.exists('rolling'):
        os.unlink('rolling')


def rollDice():
    startRolling()
    try:
        Servo.start(1.55)
        time.sleep(1)
        Servo.start(7)
        with picamera.PiCamera() as camera:
            camera.resolution = (1024, 768)
            camera.color_effects = (128, 128)
            camera.start_preview()

            # crop (x,y,w,h), values range: [0,1]
            # camera.crop = (0.53, 0.28, 0.16, 0.2)
            camera.crop = (0.56, 0.28, 0.16, 0.2)       # slightly right


            GPIO.output(CAMLED,False)
            # Camera warm-up time
            time.sleep(0.8)
            camera.capture('/opt/wrfl/img/w.jpg', resize=(60, 60))

        pip = wrfl_count.countPip()
        f = open('pip.txt', 'w')
        f.write(str(pip))
        f.close()

        pipStr = '-' + ('u' if pip == 0 else str(pip))
        target = '/opt/wrfl/img/foo-'+ str(int(time.time())) + pipStr + '.jpg'
        copyfile('/opt/wrfl/img/w.jpg', target)

        if pip > 0:
            wrfl_twitter.tweet('eine ' + str(pip))
        else:
            wrfl_twitter.tweet('unklar')

    except:
        # remove file in any case
        endRolling()

    endRolling()




def readPip():
    if os.path.exists('pip.txt'):
        f = open('pip.txt', 'r')
        pip = f.read()
        f.close()
    else:
        pip = 23

    return int(pip)



@route('/')
def index():
    timestamp = int(time.time())
    pip = readPip()

    return template('index', timestamp=timestamp, pip=pip)


@route('/wrfl')
def index():
    if isRolling():
        jsonData = json.dumps({'error': 1})
    else:
        rollDice()
        pip = readPip()
        jsonData = json.dumps({'pip':pip})

    return str(jsonData)



@route('/img/<filename>')
def server_static(filename):
    return static_file(filename, root='/opt/wrfl/img')


@route('/resources/<filename>')
def server_static(filename):
    return static_file(filename, root='/opt/wrfl/resources')


@route('/css/<filename>')
def server_static(filename):
    return static_file(filename, root='/opt/wrfl/css')



run(host='0.0.0.0', port=8080, server='paste')
#run(host='0.0.0.0', port=8080)

