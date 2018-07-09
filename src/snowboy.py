import pyaudio
import snowboydecoder
import sys
import signal
#import RPi.GPIO as GPIO
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
##### Настройки #####
#Название файлов модели.
#model1 = 'model1.pmdl'
#model2 = 'model2.pmdl'
#Путь к файлу конфигурации
home = os.path.abspath(os.path.dirname(__file__))
path = home+'/settings.ini'
config = configparser.ConfigParser()
#Приветствие
subprocess.Popen(["aplay", home+"/snd/Startup.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
interrupted = False
#Ссылки на голосовые модели
#models = [home+'/resources/'+model1, home+'/resources/'+model2]
models = []
root_dir = home+'/resources/models'
for files in os.walk(root_dir):
    for file in files:
        j = os.path.join(file)
for m in j:
    models.append("/resources/models/"+m)
# Загрузка конфига
def getConfig (path):
    try:
        global ID, TITLE, NAME, LINKEDROOM, PROVIDERTTS, APIKEYTTS, PROVIDERSTT, APIKEYSTT, SENSITIVITY1, ALARMKWACTIVATED, ALARMTTS, ALARMSTT, IP, IP_SERVER, FIRSTBOOT
        config.read(path)
        #ID = config.get("Settings", "ID") #номер терминала
        #TITLE = config.get("Settings", "TITLE") #навазние терминала
        #NAME = config.get("Settings", "NAME") #Системное имя
        #LINKEDROOM = config.get("Settings", "LINKEDROOM") #Расположение
        #IP = config.get("Settings", "IP")
        PROVIDERTTS = config.get("Settings", "PROVIDERTTS") # Сервис синтеза речи
        APIKEYTTS = config.get("Settings", "APIKEYTTS") #Ключ API сервиса синтеза речи:
        PROVIDERSTT = config.get("Settings", "PROVIDERSTT") #Сервис распознования речи
        APIKEYSTT = config.get("Settings", "APIKEYSTT") #Ключ API сервиса распознования речи:
        SENSITIVITY1 = config.get("Settings", "SENSITIVITY") #Чувствительность реагирования на ключевое слово
        ALARMKWACTIVATED = config.get("Settings", "ALARMKWACTIVATED") #Сигнал о распозновании ключевого слова
        ALARMTTS = config.get("Settings", "ALARMTTS") #Сигнал перед сообщением
        ALARMSTT = config.get("Settings", "ALARMSTT") #Сигнал перед начале распознования речи
        IP_SERVER = config.get("Settings", "IP_SERVER") #Сервер МДМ
        FIRSTBOOT = config.get("Boot", "firstboot")
        print ("Конфигурация загружена")
    except:
        say ("Не создан файл конфигурации или ошибка в файле, загрузите данные через модуль в МДМ")

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
        #snowboydecoder.play_audio_file(snowboydecoder.DETECT_DING)
        if ALARMKWACTIVATED == "1":
            subprocess.Popen(["aplay", home+"/snd/ding.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print (SENSITIVITY1)
        index = pyaudio.PyAudio().get_device_count() - 1
        print (index)
        with sr.Microphone() as source:
            r = sr.Recognizer()
            #r.adjust_for_ambient_noise(source) # Слушаем шум 1 секунду, потом распознаем, если раздажает задержка можно закомментировать.
            random_item = random.SystemRandom().choice(["Привет", "Слушаю", "На связи", "Привет-Привет"])
            say (random_item)
            audio = r.listen(source, timeout = 10)
            if ALARMTTS == "1":
                subprocess.Popen(["aplay", home+"/snd/dong.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            #snowboydecoder.play_audio_file(snowboydecoder.DETECT_DONG)
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
            #snowboydecoder.play_audio_file(snowboydecoder.DETECT_DONG)
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
            #say ("говорите после сигнала")
    except request.ConnectionResetError:
            say ("Ошибка соединения с сервером распознования речи")
    detector.start(detected_callback=callbacks,
               interrupt_check=interrupt_callback,
                sleep_time=0.03)
#Узнаем IP адрес
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]
# Загрузка конфига
getConfig (path)
#capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)
#sensitivity = [SENSITIVITY1]*len(models) #уровень распознования, чем больше значение, тем больше ложных срабатываней
sensitivity = [SENSITIVITY1] #уровень распознования, чем больше значение, тем больше ложных срабатываней
detector = snowboydecoder.HotwordDetector(models, sensitivity=sensitivity)
#callbacks = [detected, detected]
callbacks = []
for l in models:
    callbacks.append("detected")
# main loop
# make sure you have the same numbers of callbacks and models
print('Слушаю... Нажмите Ctrl+C для выхода')
detector.start(detected_callback=callbacks,
               interrupt_check=interrupt_callback,
                sleep_time=0.03)
detector.terminate()
