#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Импорт
import sys
import os
# Читаем аргумент
if len(sys.argv) == 1:
    print("Error: need to specify text")
    print("Usage: python try.py text") # pythone try.py rec_1_1
    sys.exit(-1)
# Присваем аргумент переменной
text = sys.argv[1]
# Разбираем аргумент на куски
param = text.split("_")
a = param[0] # rec, play или compile
b = param[1] # 1-6
c = param[2] # 1-3

if a == "rec":
    print ("/tmp/"+b+"/"+c+".wav")

elif a == "play":
    print ("/tmp/"+b+"/"+c+".wav")

elif a == "compile":
    print ("/resources/training_service.sh /tmp/"+b+"/1.wav /tmp/"+b+"/2.wav /tmp/"+b+"/3.wav convert to /resources/model"+b+".pmdl")


c = []
root_dir = './resources'

for files in os.walk(root_dir):
    for file in files:
        a = os.path.join(file)
for b in a:
    c.append("/resources/"+b)

print c
