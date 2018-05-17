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

##### Настройки #####
#Название файлов модели. 
model1 = 'privet-alice.pmdl'
model2 = 'alice_privet.pmdl'

home = os.path.abspath(os.path.dirname(__file__)) 
path = home+'/settings.ini'

subprocess.Popen(["aplay", home+"/snd/Startup.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

interrupted = False
#Ссылки на голосовые модели 

models = [home+'/resources/'+model1, home+'/resources/'+model2]


# Загрузка конфига 
def getConfig (path):
    try:
        global ID, TITLE, NAME, LINKEDROOM, PROVIDERTTS, APIKEYTTS, PROVIDERSTT, APIKEYSTT, SENSITIVITY, ALARMKWACTIVATED, ALARMTTS, ALARMSTT, IP, IP_SERVER
        config = configparser.ConfigParser()
        config.read(path)
        ID = config.get("Settings", "ID") #номер терминала
        TITLE = config.get("Settings", "TITLE") #навазние терминала 
        NAME = config.get("Settings", "NAME") #Системное имя
        LINKEDROOM = config.get("Settings", "LINKEDROOM") #Расположение 
        IP = config.get("Settings", "IP")
        PROVIDERTTS = config.get("Settings", "PROVIDERTTS") # Сервис синтеза речи
        APIKEYTTS = config.get("Settings", "APIKEYTTS") #Ключ API сервиса синтеза речи:
        PROVIDERSTT = config.get("Settings", "PROVIDERSTT") #Сервис распознования речи
        APIKEYSTT = config.get("Settings", "APIKEYSTT") #Ключ API сервиса распознования речи:
        SENSITIVITY = config.get("Settings", "SENSITIVITY") #Чувствительность реагирования на ключевое слово
        ALARMKWACTIVATED = config.get("Settings", "ALARMKWACTIVATED") #Сигнал о распозновании ключевого слова
        ALARMTTS = config.get("Settings", "ALARMTTS") #Сигнал перед сообщением
        ALARMSTT = config.get("Settings", "ALARMSTT") #Сигнал перед начале распознования речи
        IP_SERVER = config.get("Settings", "IP_SERVER") #Сервер МДМ
        FIRSTBOOT = config.get("Settings", "firstboot")
        print ("Конфигурация загружена")
        
    except:
        print ("Не создан файл конфигурации или ошибка в файле, загрузите данные через модуль в МДМ")

def signal_handler(signal, frame):
    global interrupted
    interrupted = True



def interrupt_callback():
    global interrupted
    return interrupted

def detected():
   try:
       getConfig (path)
       #snowboydecoder.play_audio_file(snowboydecoder.DETECT_DING)
       if ALARMKWACTIVATED == "1":
           subprocess.Popen(["aplay", home+"/snd/ding.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
       index = pyaudio.PyAudio().get_device_count() - 1
       print (index)
       r = sr.Recognizer()
       with sr.Microphone(device_index=2) as source:
           r.adjust_for_ambient_noise(source) # Слушаем шум 1 секунду, потом распознаем, если раздажает задержка можно закомментировать. 
           random_item = random.SystemRandom().choice(["Привет", "Слушаю", "На связи", "Привет-Привет"])
           say (random_item)
           audio = r.listen(source, timeout = 10)
           if ALARMTTS == "1":
               subprocess.Popen(["aplay", home+"/snd/dong.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
           #snowboydecoder.play_audio_file(snowboydecoder.DETECT_DONG)
           print("Processing ... Для распознования используем "+PROVIDERSTT)
           #
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
           random_item = random.SystemRandom().choice(["Вы что то сказали ?", "Я ничего не услышала", "Что Вы спросили?", "Не поняла"])
           say (random_item)


   except sr.RequestError as e:
           say ("Произошла ошибка  {0}".format(e))

   except sr.WaitTimeoutError:
           random_item = random.SystemRandom().choice(["Вы что то сказали ?", "Я ничего не услышала", "Что Вы спросили?", "Не поняла"])
           say (random_item)
           #say ("говорите после сигнала")
           #detected()

# Загрузка конфига 
getConfig (path)
#capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

sensitivity = [SENSITIVITY]*len(models) #уровень распознования, чем больше значение, тем больше ложных срабатываней 
detector = snowboydecoder.HotwordDetector(models, sensitivity=sensitivity)
callbacks = [detected, detected]

print('Слушаю... Нажмите Ctrl+C для выхода')

# main loop
# make sure you have the same numbers of callbacks and models
detector.start(detected_callback=callbacks,
               interrupt_check=interrupt_callback,
               sleep_time=0.03)

detector.terminate()
