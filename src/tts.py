from gtts import gTTS
from googletrans import Translator
from yandex_speech import TTS
import requests
import os
import os.path
import hashlib
import configparser

##Speech and translator declarations
home = os.path.abspath(os.path.dirname(__file__))
path = home+'/settings.ini'

words = '1'
ttsfilename=home+"/snd/" + words + ".wav"
translator = Translator()
language='ru-RU'
languageG='ru'

#Text to speech converter with translation
def say(words):
#    words= translator.translate(words, dest=language)
#    words=words.text
#    words=words.replace("Text, ",'',1)
#    words=words.strip()
    print(words)
    getConfig (path)
    md5 = hashlib.sha1(words.encode('utf-8')).hexdigest()
    filemp3 = ""
    for file in os.listdir(home+"/snd/"):
        if file.endswith(md5+".wav"):
          filemp3 = (os.path.join(file))

    if filemp3 == md5+".wav":
      print ("Файл уже записан")
      os.system("aplay -q "+home+"/snd/"+ filemp3)
    elif filemp3 == md5+".mp3":
      print ("Файл уже записан")
      s.system("mpg123 -q "+filemp3)

    elif PROVIDERTTS == "Yandex":
      print ("Генерируем файл")
      #tts = gTTS(text=words, lang=languageG)
      tts = TTS("alyss", "wav", APIKEYTTS, lang=language,emotion="good")
      tts.generate(words)
      words = hashlib.sha1(words.encode('utf-8')).hexdigest()
      ttsfilename=home+"/snd/" + words + ".wav"
      tts.save(ttsfilename)
      os.system("aplay -q "+ttsfilename)
      #os.remove(ttsfilename)

    elif PROVIDERTTS == "Google":
      print ("Генерируем файл")
      tts = gTTS(text=words, lang=languageG)
      words = hashlib.sha1(words.encode('utf-8')).hexdigest()
      ttsfilename=home+"/snd/" + words + ".mp3"
      tts.save(ttsfilename)
      os.system("mpg123 -q "+ttsfilename)
      #os.remove(ttsfilename)

def getConfig (path):
    try:
        global ID, TITLE, NAME, LINKEDROOM, PROVIDERTTS, APIKEYTTS, PROVIDERSTT, APIKEYSTT, SENSITIVITY, ALARMKWACTIVATED, ALARMTTS, ALARMSTT, IP
        config = configparser.ConfigParser()
        config.read(path)
        PROVIDERTTS = config.get("Settings", "PROVIDERTTS") # Сервис синтеза речи
        APIKEYTTS = config.get("Settings", "APIKEYTTS") #Ключ API сервиса синтеза речи:
    except:
        print ("Не создан файл конфигурации или ошибка в файле, загрузите данные через модуль в МДМ")

getConfig (path)
