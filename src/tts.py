from gtts import gTTS
from googletrans import Translator
from yandex_speech import TTS
import requests
import os
import os.path
import hashlib

##Speech and translator declarations
words = '1'
ttsfilename="/tmp/" + words + ".wav"
translator = Translator()
language='ru-RU'
key = "3a5d503c-d9a8-489d-a100-954294c36cf8"




#Text to speech converter with translation
def say(words):
#    words= translator.translate(words, dest=language)
#    words=words.text
#    words=words.replace("Text, ",'',1)
#    words=words.strip()
    print(words)
    md5 = hashlib.sha1(words.encode('utf-8')).hexdigest()
    filemp3 = ""
    for file in os.listdir("/tmp/"):
        if file.endswith(md5+".mp3"):
          filemp3 = (os.path.join(file))
		  
    if filemp3 == md5+".wav":
      os.system("aplay -q /tmp/"+ filemp3)
      print ("Файл уже записан") 
    else:
      print ("Генерируем файл") 
      #tts = gTTS(text=words, lang=language)
      tts = TTS("alyss", "wav", key, lang=language,emotion="good")
      tts.generate(words)
      words = hashlib.sha1(words.encode('utf-8')).hexdigest()
      ttsfilename="/tmp/" + words + ".wav"
      tts.save(ttsfilename)
      os.system("aplay -q "+ttsfilename)
      #os.remove(ttsfilename)
    
