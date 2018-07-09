# Импорт
import sys
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
    try:
        print ("/tmp/"+b+"/"+c+".wav")
    except subprocess.TimeoutExpired:
        print ("Fail")

elif a == "play":
    print ("/tmp/"+b+"/"+c+".wav")

elif a == "compile":
    if b == "1":
        try:
            print ("/resources/training_service.sh /tmp/1/1.wav /tmp/1/2.wav /tmp/1/3.wav convert to /resources/model"+b+".pmdl")
        except:
            print ("Fail")
    elif b == "2":
        try:
            print ("/resources/training_service.sh /tmp/2/1.wav /tmp/2/2.wav /tmp/2/3.wav convert to /resources/model"+b+".pmdl")
        except:
            print ("Fail")
    elif b == "3":
        try:
            print ("/resources/training_service.sh /tmp/3/1.wav /tmp/3/2.wav /tmp/3/3.wav convert to /resources/model"+b+".pmdl")
        except:
            print ("Fail")
    elif b == "4":
        try:
            print ("/resources/training_service.sh /tmp/4/1.wav /tmp/4/2.wav /tmp/4/3.wav convert to /resources/model"+b+".pmdl")
        except:
            print ("Fail")
    elif b == "5":
        try:
            print ("/resources/training_service.sh /tmp/5/1.wav /tmp/5/2.wav /tmp/5/3.wav convert to /resources/model"+b+".pmdl")
        except:
            print ("Fail")
    elif b == "6":
        try:
            print ("/resources/training_service.sh /tmp/6/1.wav /tmp/6/2.wav /tmp/6/3.wav convert to /resources/model"+b+".pmdl")
        except:
            print ("Fail")
