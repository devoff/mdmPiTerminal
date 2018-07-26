import pyaudio
import snowboydecoder
import sys
import signal
import time
import os
import subprocess
import speech_recognition as sr
import urllib.request
from tts import say
import configparser
import random
import socket
import fcntl
import struct

home = os.path.abspath(os.path.dirname(__file__))
path = home+'/settings.ini'
config = configparser.ConfigParser()
interrupted = False
models = []
root_dir = home+'/resources/models/'
for files in os.walk(root_dir):
    for m in files[2]:
        models.append(home+'/resources/models/'+m)

def getConfig (path):
    try:
        global PROVIDERTTS, APIKEYTTS, PROVIDERSTT, APIKEYSTT, SENSITIVITY, ALARMKWACTIVATED, ALARMTTS, ALARMSTT, IP_SERVER
        config.read(path)
        PROVIDERTTS = config.get("Settings", "PROVIDERTTS") # Сервис синтеза речи
        APIKEYTTS = config.get("Settings", "APIKEYTTS") #Ключ API сервиса синтеза речи:
        PROVIDERSTT = config.get("Settings", "PROVIDERSTT") #Сервис распознования речи
        APIKEYSTT = config.get("Settings", "APIKEYSTT") #Ключ API сервиса распознования речи:
        SENSITIVITY = config.get("Settings", "SENSITIVITY") #Чувствительность реагирования на ключевое слово
        ALARMKWACTIVATED = config.get("Settings", "ALARMKWACTIVATED") #Сигнал о распозновании ключевого слова
        ALARMTTS = config.get("Settings", "ALARMTTS") #Сигнал перед сообщением
        ALARMSTT = config.get("Settings", "ALARMSTT") #Сигнал перед начале распознования речи
        IP_SERVER = config.get("Settings", "IP_SERVER") #Сервер МДМ
        print ("Конфигурация загружена")
    except:
        say ("Не создан файл конфигурации или ошибка в файле, загрузите данные через модуль в МДМ")
        sys.exit(0)

def signal_handler(signal, frame):
    global interrupted
    interrupted = True

def interrupt_callback():
    global interrupted
    return interrupted

def detected():
    try:
        getConfig (path)
        detector.terminate()
        if ALARMKWACTIVATED == "1":
            subprocess.Popen(["aplay", home+"/snd/ding.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print (SENSITIVITY)
        #index = pyaudio.PyAudio().get_device_count() - 1
        #print (index)
        with sr.Microphone() as source:
            r = sr.Recognizer()
            r.adjust_for_ambient_noise(source) # Слушаем шум 1 секунду, потом распознаем, если раздажает задержка можно закомментировать.
            random_item = random.SystemRandom().choice(["Привет", "Слушаю", "На связи", "Привет-Привет"])
            say (random_item)
            audio = r.listen(source, timeout = 10, phrase_time_limit=15)
            if ALARMTTS == "1":
                subprocess.Popen(["aplay", home+"/snd/dong.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("Processing ... Для распознования используем "+PROVIDERSTT)
            if PROVIDERSTT == "Google":
                command=r.recognize_google(audio, language="ru-RU")
            elif PROVIDERSTT == "Wit.ai":
                command=r.recognize_wit(audio, key=APIKEYSTT)
            elif PROVIDERSTT == "Microsoft":
                command=r.recognize_bing(audio, key=APIKEYSTT)
            print(command)
            if ALARMTTS == "1":
               subprocess.Popen(["aplay", home+"/snd/dong.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            link="http://"+IP_SERVER+'/command.php?qry=' + urllib.parse.quote_plus(command)
            f=urllib.request.urlopen(link)
    except  sr.UnknownValueError:
            random_item = random.SystemRandom().choice(["Вы что то сказали?", "Я ничего не услышала", "Что Вы спросили?", "Не поняла"])
            say (random_item)
    except sr.RequestError as e:
            say ("Произошла ошибка  {0}".format(e))
    except sr.WaitTimeoutError:
            random_item = random.SystemRandom().choice(["Вы что то сказали ?", "Я ничего не услышала", "Что Вы спросили?", "Не поняла"])
            say (random_item)
    except request.ConnectionResetError:
            say ("Ошибка соединения с сервером распознования речи")
    detector.start(detected_callback=callbacks,
               interrupt_check=interrupt_callback,
                sleep_time=0.03)

getConfig (path)
signal.signal(signal.SIGINT, signal_handler)
sensitivity = [SENSITIVITY]
detector = snowboydecoder.HotwordDetector(models, sensitivity=sensitivity)
callbacks = []
for l in models:
    callbacks.append(detected)

print('Слушаю... Нажмите Ctrl+C для выхода')
detector.start(detected_callback=callbacks,
               interrupt_check=interrupt_callback,
                sleep_time=0.03)
detector.terminate()
