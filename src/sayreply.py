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
#busy = os.system("ps aux|grep 'aplay'|grep -v grep |awk '{print $2}'")

def detected():
   try:
       getConfig (path)
       if ALARMKWACTIVATED == "1":
           subprocess.Popen(["aplay", home+"/snd/ding.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
       #index = pyaudio.PyAudio().get_device_count() - 1
       #print (index)
       with sr.Microphone() as source:
           r = sr.Recognizer()
           r.adjust_for_ambient_noise(source) # Слушаем шум 1 секунду, потом распознаем, если раздажает задержка можно закомментировать.
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
   except  sr.UnknownValueError as e:
           print("Произошла ошибка  {0}".format(e))
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
       os.system("sudo service mdmpiterminal stop")
       say(text)
       detected()
       os.system("sudo service mdmpiterminal start")
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
        param = text.split("_") # должно быть вида rec_1_1, play_2_1, compile_5_1
        a = param[0] # rec, play или compile
        b = param[1] # 1-6
        c = param[2] # 1-3
        if a == "rec":
           os.system("sudo service mdmpiterminal stop")
           say ("Запись на 5 секунд начнется после голосового сигнала")
           try:
               subprocess.Popen(["aplay", home+"/snd/ding.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
               sleep(0.3)
               subprocess.call(["rec", "/tmp/"+b+c+".wav"], timeout = 5)
           except subprocess.TimeoutExpired:
               subprocess.Popen(["aplay", home+"/snd/ding.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
               sleep(0.3)
               say ("Запись файла завершена")
               os.system("sudo service mdmpiterminal start")
        elif a == "play":
           os.system("aplay /tmp/"+b+c+".wav")

        elif a == "compile":
           say ("Отправляю модель на обработку");
           try:
               os.system(home+"/resources/training_service.sh /tmp/"+b+"1.wav /tmp/"+b+"2.wav /tmp/"+b+"3.wav "+home+"/resources/models/model"+b+".pmdl")
               print (home+"/resources/training_service.sh /tmp/"+b+"1.wav /tmp/"+b+"2.wav /tmp/"+b+"3.wav convert to /resources/models/model"+b+".pmdl")
               say ("Модель голоса создана успешно");
           except:
               say ("Произошла ошибка при отправке");
        elif a == "save":
            say ("Идет подготовка к перезагрузке");
            sleep(0.3)
            try:
                os.system("sudo service mdmpiterminal restart")
                say ("Готово")
            except:
                say ("Что-то пошло не так");

def getConfig (path):
    try:
        global PROVIDERTTS, APIKEYTTS, PROVIDERSTT, APIKEYSTT, ALARMKWACTIVATED, ALARMTTS, ALARMSTT, IP_SERVER, FIRSTBOOT
        config = configparser.ConfigParser()
        config.read(path)
        PROVIDERTTS = config.get("Settings", "PROVIDERTTS") # Сервис синтеза речи
        APIKEYTTS = config.get("Settings", "APIKEYTTS") #Ключ API сервиса синтеза речи:
        PROVIDERSTT = config.get("Settings", "PROVIDERSTT") #Сервис распознования речи
        APIKEYSTT = config.get("Settings", "APIKEYSTT") #Ключ API сервиса распознования речи:
        #SENSITIVITY = config.get("Settings", "SENSITIVITY") #Чувствительность реагирования на ключевое слово
        ALARMKWACTIVATED = config.get("Settings", "ALARMKWACTIVATED") #Сигнал о распозновании ключевого слова
        ALARMTTS = config.get("Settings", "ALARMTTS") #Сигнал перед сообщением
        ALARMSTT = config.get("Settings", "ALARMSTT") #Сигнал перед начале распознования речи
        IP_SERVER = config.get("Settings", "IP_SERVER") #Сервер МДМ
        FIRSTBOOT = config.get("Boot", "firstboot")
        print ("Конфигурация загружена")
    except:
        say ("Не создан файл конфигурации или ошибка в файле, загрузите данные через модуль в МДМ")
        sys.exit(0)
        
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

getConfig (path)
if FIRSTBOOT == "1":
    ip = (get_ip_address())
    say ("Это первая загрузка терминала, мой IP адрес: "+ip)
elif FIRSTBOOT == "0":
    say ("Терминал готов к работе")

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
