#####
#rec_1_1
#play_1_1
#compile_1_1
#####

text = "rec_1_1"

param = text.split("_")
a = param[0]
b = param[1]
c = param[2]

if a == "rec":
    try:
        subprocess.Popen(["aplay", home+"/snd/ding.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        sleep(0.3)
        subprocess.call(["rec", "/tmp/"+b+c+".wav"], timeout = 5)
    except subprocess.TimeoutExpired:
        subprocess.Popen(["aplay", home+"/snd/ding.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        sleep(0.3)
        print ("Fail")

elif a == "play":
    os.system("aplay /tmp/"+b+c+".wav")

elif a == "compile":
    if c == "1":
        try:
            os.system(home+"/resources/training_service.sh /tmp/11.wav /tmp/12.wav /tmp/13.wav "+home+"/resources/model"+c+".pmdl")
            print (home+"/resources/training_service.sh /tmp/11.wav /tmp/12.wav /tmp/13.wav "+home+"/resources/model"+c+".pmdl")
            print ("OK")
        except:
            print ("Fail")
    elif c == "2":
        try:
            os.system(home+"/resources/training_service.sh /tmp/21.wav /tmp/22.wav /tmp/23.wav "+home+"/resources/model"+c+".pmdl")
            print (home+"/resources/training_service.sh /tmp/21.wav /tmp/22.wav /tmp/23.wav "+home+"/resources/model"+c+".pmdl")
            print ("OK")
        except:
            print ("Fail")
