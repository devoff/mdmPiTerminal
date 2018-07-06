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
import fcntl
import struct
import urllib.request

home = os.path.abspath(os.path.dirname(__file__))
path = home+'/settings.ini'






def detected():
   try:
       getConfig (path)
       if ALARMKWACTIVATED == "1":
           subprocess.Popen(["aplay", home+"/snd/ding.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
       index = pyaudio.PyAudio().get_device_count() - 1
       print (index)
       r = sr.Recognizer()
       with sr.Microphone(index) as source:
           #r.adjust_for_ambient_noise(source) # Слушаем шум 1 секунду, потом распознаем, если раздажает задержка можно закомментировать.

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
           link="http://"+IP_SERVER+'/command.php?qry=' + urllib.parse.quote_plus(command)
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
       config.add_section("Boot")
       config.set("Boot", "firstboot", "0" )
       with open(path, "w") as config_file:
           config.write(config_file)
       getConfig (path)
    if method == 'rec' :
        if text == "rec1_1":
           say ("Запись на 5 секунд начнется после голосового сигнала")
       #os.system("rec -r 16000 -c 1 -b 16 -e signed-integer /tmp/1.wav")
           try:
               subprocess.Popen(["aplay", home+"/snd/ding.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
               sleep(0.3)
               subprocess.call(["rec", "/tmp/1.wav"], timeout = 5)

           except subprocess.TimeoutExpired:
               subprocess.Popen(["aplay", home+"/snd/ding.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
               sleep(0.3)
               say ("Запись первого файла завершена")

        elif text == "rec1_2":
           try:
               subprocess.Popen(["aplay", home+"/snd/ding.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
               sleep(0.3)
               subprocess.call(["rec", "/tmp/2.wav"], timeout = 5)
           except subprocess.TimeoutExpired:
               subprocess.Popen(["aplay", home+"/snd/ding.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
               sleep(0.3)
               say ("Запись второго файла завершена")

        elif text == "rec1_3":
           try:
               subprocess.Popen(["aplay", home+"/snd/ding.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
               sleep(0.3)
               subprocess.call(["rec", "/tmp/3.wav"], timeout = 5)
           except subprocess.TimeoutExpired:
               subprocess.Popen(["aplay", home+"/snd/ding.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
               sleep(0.3)
               say ("Запись третьего файла завершена")

        elif text == "play1_1":
           os.system("aplay /tmp/1.wav")
        elif text == "play1_2":
           os.system("aplay /tmp/2.wav")
        elif text == "play1_3":
           os.system("aplay /tmp/3.wav")
        elif text == "compile1":
           say ("Отправляю модель на обработку");
           try:
               os.system(home+"/resources/training_service.sh /tmp/1.wav /tmp/2.wav /tmp/3.wav "+home+"/resources/model1.pmdl")
               print (home+"/resources/training_service.sh /tmp/1.wav /tmp/2.wav /tmp/3.wav "+home+"/resources/model1.pmdl")
               say ("Модель голоса создана успешно");
           except:
               say ("Произошла ошибка при отправке");

def getConfig (path):
    try:
        global ID, TITLE, NAME, LINKEDROOM, PROVIDERTTS, APIKEYTTS, PROVIDERSTT, APIKEYSTT, SENSITIVITY, ALARMKWACTIVATED, ALARMTTS, ALARMSTT, IP, IP_SERVER, FIRSTBOOT
        config = configparser.ConfigParser()
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
        SENSITIVITY = config.get("Settings", "SENSITIVITY") #Чувствительность реагирования на ключевое слово
        ALARMKWACTIVATED = config.get("Settings", "ALARMKWACTIVATED") #Сигнал о распозновании ключевого слова
        ALARMTTS = config.get("Settings", "ALARMTTS") #Сигнал перед сообщением
        ALARMSTT = config.get("Settings", "ALARMSTT") #Сигнал перед начале распознования речи
        IP_SERVER = config.get("Settings", "IP_SERVER") #Сервер МДМ
        FIRSTBOOT = config.get("Boot", "firstboot")
        print ("Конфигурация загружена")


    except:
        print ("Не создан файл конфигурации или ошибка в файле, загрузите данные через модуль в МДМ")

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', bytes(ifname[:15], 'utf-8'))
    )[20:24])

getConfig (path)
if FIRSTBOOT == "1":
    ip = (get_ip_address('eth0'))
    say ("Это первая загрузка терминала, мой IP адрес: "+ip)
#    config.set("Boot", "firstboot", "0" )
#    with open(path, "w") as config_file:
#        config.write(config_file)
#    getConfig (path)
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
