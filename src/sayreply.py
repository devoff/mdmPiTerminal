#!/usr/bin/env python3

import time
import socket
import pyaudio
import snowboydecoder
import subprocess
import os
import speech_recognition as sr
import json
import configparser
from urllib.parse import unquote
from tts import say
from time import sleep

import urllib.request

home = os.path.abspath(os.path.dirname(__file__)) 
path = home+'/settings.ini'
#Адрес до MajorDomo 
urlmjd = 'http://192.168.2.62'






def detected():
   try:
       getConfig (path)
       if ALARMKWACTIVATED == "1":
           subprocess.Popen(["aplay", home+"/snd/ding.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
       index = pyaudio.PyAudio().get_device_count() - 1
       print (index)
       r = sr.Recognizer()
       with sr.Microphone(index) as source:
           r.adjust_for_ambient_noise(source) # Слушаем шум 1 секунду, потом распознаем, если раздажает задержка можно закомментировать. 
           
           audio = r.listen(source, timeout = 10)
           if ALARMTTS == "1":
               subprocess.Popen(["aplay", home+"/snd/dong.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
           #snowboydecoder.play_audio_file(snowboydecoder.DETECT_DONG)
           print("Processing !")
           #command=r.recognize_wit(audio, key="2S2VKVFO5X7353BN4X6YBX56L4S2IZT4")
           command=r.recognize_google(audio, language="ru-RU")
           print(command)
           if ALARMSTT == "1":
               subprocess.Popen(["aplay", home+"/snd/dong.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
           #snowboydecoder.play_audio_file(snowboydecoder.DETECT_DONG)
           link=IP_SERVER+'/command.php?qry=' + urllib.parse.quote_plus(command)
           f=urllib.request.urlopen(link)
   except  sr.UnknownValueError as e:
           print("Произошла ошибка  {0}".format(e))
		   #detected ()
   except sr.RequestError as e:
           print("Произошла ошибка  {0}".format(e))
           say ("Произошла ошибка  {0}".format(e))

   except sr.WaitTimeoutError:
           print ("Я ничего не услышала")
           say ("Я ничего не услышала")

		   



def parse(conn, addr):# обработка соединения в отдельной функции
    data = b""
    
    while not b"\r\n" in data: # ждём первую строку
        tmp = conn.recv(1024)
		
        if not tmp:   # сокет закрыли, пустой объект
            #print ("tmp error")
            break
        else:
            data += tmp
            print ("OK tmp")
    
    if not data:      # данные не пришли
        return        # не обрабатываем
        
    udata = data.decode("utf-8")
    # берём только первую строку
    udata = udata.split("\r\n", 1)[0]
    print (udata)
    # разбиваем по пробелам нашу строку
    method, text = udata.split(":", maxsplit=1)
    if method == 'tts' :
       sleep(0.5)
       say (text)
    if method == 'ask' :
       detected()
    if method == 'settings' : 
       settings = text
       translation_table = dict.fromkeys(map(ord, '{"}'), None)
       settings = settings.translate(translation_table)
       settings = (settings.split(','))
       config = configparser.ConfigParser()
       config.add_section("Settings")
       for temp in settings: 
           obj, param = temp.split(":", maxsplit=1)
           config.set("Settings", obj, param)
           print (obj+":"+param)
           
       with open(path, "w") as config_file:
           config.write(config_file) 
       getConfig (path)
    if method == 'rec' :
        if text == "rec1_1": 
            say ("Запись начнется после голосового сигнала")		
       #os.system("rec -r 16000 -c 1 -b 16 -e signed-integer /tmp/1.wav")
           try: 
               subprocess.Popen(["aplay", home+"/snd/ding.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
               subprocess.call(["rec", "/tmp/1.wav"], timeout = 5)

           except subprocess.TimeoutExpired:
               subprocess.Popen(["aplay", home+"/snd/ding.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
               print ("Запись первого файла завершена")
           
        elif text == "rec1_2":
           try: 
               subprocess.Popen(["aplay", home+"/snd/ding.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
               subprocess.call(["rec", "/tmp/2.wav"], timeout = 5)
           except subprocess.TimeoutExpired:
               subprocess.Popen(["aplay", home+"/snd/ding.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
               print ("Запись второго файла завершена")
               
        elif text == "rec1_3":
           try: 
               subprocess.Popen(["aplay", home+"/snd/ding.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
               subprocess.call(["rec", "/tmp/3.wav"], timeout = 5)
           except subprocess.TimeoutExpired:
               subprocess.Popen(["aplay", home+"/snd/ding.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
               print ("Запись третьего файла завершена")
            
        elif text == "play1":
           os.system("aplay /tmp/1.wav") 
        elif text == "play2":
           os.system("aplay /tmp/2.wav") 
        elif text == "play3":
           os.system("aplay /tmp/3.wav") 
        elif text == "compile":
           say ("Отправляю модель на обработку");
           os.system("python2 "+home+"/resources/training_service.py /tmp/1.wav /tmp/2.wav /tmp/3.wav "+home+"/resources/model1.pmdl") 
           #print ("python "+home+"/resources/training_service.py /tmp/1.wav /tmp/2.wav /tmp/3.wav"+home+" /resources/model1.pmdl")
           say ("Модель голоса создана успешно");

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
        print ("Конфигурация загружена")
        
    except:
        print ("Не создан файл конфигурации или ошибка в файле, загрузите данные через модуль в МДМ")


getConfig (path)   	   
sock = socket.socket()
sock.bind( ("", 7999) )
sock.listen(1)


try:
    while 1: # работаем постоянно
        conn, addr = sock.accept()
        conn.settimeout(2.0)
        print("New connection from " + addr[0])
        try:
            parse(conn, addr)

        except socket.timeout:
            print (addr, "timeout")
        
		
        finally:
            # так при любой ошибке
            # сокет закроем корректно
            conn.close()
finally: sock.close()
# так при возникновении любой ошибки сокет
# всегда закроется корректно и будет всё хорошо