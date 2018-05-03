#!/usr/bin/env python3

import time
import socket
import pyaudio
import snowboydecoder
import subprocess
import os
import speech_recognition as sr
from urllib.parse import unquote
from tts import say

home = os.path.abspath(os.path.dirname(__file__)) 

def detected():
   try:
       #snowboydecoder.play_audio_file(snowboydecoder.DETECT_DING)
       subprocess.Popen(["aplay", home+"/snd/ding.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
       index = pyaudio.PyAudio().get_device_count() - 1
       print (index)
       r = sr.Recognizer()
       with sr.Microphone(index) as source:
           r.adjust_for_ambient_noise(source) # Слушаем шум 1 секунду, потом распознаем, если раздажает задержка можно закомментировать. 
           
           audio = r.listen(source, timeout = 10)
           subprocess.Popen(["aplay", home+"/snd/dong.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
           #snowboydecoder.play_audio_file(snowboydecoder.DETECT_DONG)
           print("Processing !")
           #command=r.recognize_wit(audio, key="2S2VKVFO5X7353BN4X6YBX56L4S2IZT4")
           command=r.recognize_google(audio, language="ru-RU")
           print(command)
           subprocess.Popen(["aplay", home+"/snd/dong.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
           #snowboydecoder.play_audio_file(snowboydecoder.DETECT_DONG)
           #link=urlmjd+'/command.php?qry=' + urllib.parse.quote_plus(command)
           #f=urllib.request.urlopen(link)
   except  sr.UnknownValueError:
           print("Произошла ошибка  {0}".format(e))
		   #detected ()
   except sr.RequestError as e:
           print("Произошла ошибка  {0}".format(e))
           say ("Произошла ошибка  {0}".format(e))

   except sr.WaitTimeoutError:
           print ("Я ничего не услышала")
           say ("Я ничего не услышала")

		   

def send_answer(conn, status="200 OK", typ="text/plain; charset=utf-8", data=""):
    data = data.encode("utf-8")
    conn.send(b"HTTP/1.1 " + status.encode("utf-8") + b"\r\n")
    conn.send(b"Server: simplehttp\r\n")
    conn.send(b"Connection: close\r\n")
    conn.send(b"Content-Type: " + typ.encode("utf-8") + b"\r\n")
    conn.send(b"Content-Length: " + bytes(len(data)) + b"\r\n")
    conn.send(b"\r\n")# после пустой строки в HTTP начинаются данные
    conn.send(data)
    #detected ()

def parse(conn, addr):# обработка соединения в отдельной функции
    data = b""
    
    while not b"\r\n" in data: # ждём первую строку
        tmp = conn.recv(1024)
        print ("OK")
        if not tmp:   # сокет закрыли, пустой объект
            print ("tmp error")
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
    method, address, protocol = udata.split(" ", 2)
    text = address[address.find("text=")+5:]
    text = unquote(text)
    #text = urllib.unquote(text).decode('utf8') 
    #text  = address.split("text=", 2)
    #print (text)
    say (text)
    
	
	
    if method != "GET" :
        send_answer(conn, "404 Not Found", data="Не найдено")
        return

    answer = """<!DOCTYPE html>"""
    answer += """<html><head><title>Время</title></head><body>"""
    answer +=  text
    answer += """</body></html>"""
     
    send_answer(conn, typ="text/html; charset=utf-8", data=answer)
    

sock = socket.socket()
sock.bind( ("", 8091) )
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
        except:
            send_answer(conn, "500 Internal Server Error", data="Ошибка")
		
        finally:
            # так при любой ошибке
            # сокет закроем корректно
            conn.close()
finally: sock.close()
# так при возникновении любой ошибки сокет
# всегда закроется корректно и будет всё хорошо