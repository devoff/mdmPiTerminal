@@ -8,6 +8,71 @@
**3. Ответ в терминал через sayReply**
**4. Подключение светодиодов (в разработке) **

!!!! На данный момент протестировано на платах - 
Orange Pi Zero - Armbian Ubuntu_xenial_default ядро 3.4 
Orange Pi Zero - Armbian Ubuntu_xenial_next ядро 4.14 (обратите внимания в разделе подготовка) 

*************************************************
## **Подготовка** 
*************************************************
Скачать и записать образ системы.
После первой загрузки системы идет долгое обновление всех пакетов, проверить можно через команду htop, будет запущен процесс dkpg  

Если ситема на Armbian Xenial mainline kernel 4.14
Обновите всю систему через apt upgrade
нужно зайти в armbian-config -> System -> Hardware: выбрать analog-audio (пробелом)
запустить alsamixer, под каждым миксером проверить, что буквы ММ(XX) горят зеленым, если нет включить (клавиша M) 
за громкость звука отвечает 2 ползунка  Line Out и DAC 

Отредактировать или создать файл /etc/asound.conf
Заранее проверить на каком усройстве микрофон и динмаик через команду 
aplay -l 
arecored -l
и отредактировать если нужно в hw:1,0 

```
sudo nano /etc/asound.conf

```
Вставить код 

```
pcm.!default {
type asym
playback.pcm "playback"
capture.pcm "capture"
}

pcm.playback {
type plug
slave.pcm "dmixed"
}

pcm.capture {
type plug
slave.pcm "hw:1,0"
}

pcm.dmixed {
type dmix
slave.pcm "hw:0,0"
ipc_key 555555
}

pcm.array {
type dsnoop
slave {
pcm "hw:0,0"
channels 2
}
ipc_key 666666
}

```
сохранить и проверить вывод звука через команду  speaker-test



*************************************************
## **Установка** 
*************************************************
@ -24,27 +89,25 @@ chmod +x scripts/mdm-pi-installer.sh


**************************************************
## **Запуск терминала как сервис с автозагрузкой** 
## **Первый запуск, подготовка терминала** 
**************************************************

```
cd ..
chmod +x systemd/service-installer.sh
sudo ./systemd/service-installer.sh

sudo systemctl enable mdmpiterminal.service
sudo systemctl enable mdmpiterminalsayreply.service

sudo systemctl start mdmpiterminalsayreply.service

ifconfig #Узнаем IP адрес терминала
sudo systemctl start mdmpiterminalsayreply.service 
```
При первом запуске терминал скажет свой IP адрес, который нужно будет добавить в МДМ (если не успели записать, воспользуйтесь командой ifconfig) 


*************************************************
## **Настройка терминала** 
************************************************
Заходим в Панель управления MajorDomo > Система > Маркет дополнений > Оборудование > Умная колонка для Мажордомо и устанавливаем модуль. 
Заходим в Панель управления MajorDomo > Система > Маркет дополнений > Оборудование > MDM VoiceAssistant и устанавливаем модуль. 

После заходим - в Нстройки > Терминалы > Добавить новую запись > Добавляем название и IP адрес терминала 

@ -57,77 +120,47 @@ ifconfig #Узнаем IP адрес терминала

Чувствительность реагирования на ключевое слово - чем больше тем лучше слышит, но будет много ложных срабатываней.  



Сохраняем

*************************************************
## **Запись ключевого слова** 
*************************************************

Я бы рекомендовал записать образцы голоса сразу на терминале с тем микрофоном, который будет использоваться, либо записать на сайте snowboy
для этого нужно получиться пройти регистрация на сайте https://snowboy.kitt.ai/ в разделе "Профиль" получить API и прописать его в файле raining_service.py 
для этого нужно получиться пройти регистрация на сайте https://snowboy.kitt.ai/

```
nano ~/mdmPiTerminal/src/resources/training_service.py
```
В МДМ в настройках модуля, во вкладка запись ключевого слово нажимаем - ЗАПИСЬ, на терминале включится запись на 5 секунд и автоматически завершиться, 
нужно повторить эту процендуру 3 раза  после отправить на компиляцию. 

Далее нужно записать 3 wav файла, после записи ctrl+c 
После записать дополнительные ключевые слова. 

*************************************************
## **Запуск терминала ** 
*************************************************

```
cd src/resources/
rec -r 16000 -c 1 -b 16 -e signed-integer 1.wav
ctrl+c 
rec -r 16000 -c 1 -b 16 -e signed-integer 2.wav
ctrl+c 
rec -r 16000 -c 1 -b 16 -e signed-integer 3.wav
ctrl+c 
```
Запускаем скрипт отправки записей для преобразования их в модель 
sudo systemctl start mdmpiterminal.service
```
python2 training_service.py 1.wav 2.wav 3.wav alice_privet.pmdl 
````

*************************************************
## **Настройка** 
## **Отладка** 
*************************************************
Для ручного запуска скриптом терминала - 

Теперь нужно прописать модели в файле src/snowboy.py и заменить IP адрес МДМ
в скрипте стоит 2 модели, если меньше нужно убрать в 83 строке один  detected если больше то добавить  ( callbacks = [detected, detected] )

```
cd ..
nano snowboy.py
```
Теперь нужно отредактировать файл озвучки, указав API yandex 
```
nano tts.py
```
Остановить сервисы 

теперь можно попробовать запустить 
```
cd ..
source env/bin/activate # Активируем виртуализацию  питона
python src/snowboy.py
sudo service mdmpiterminal stop
sudo service mdmpiterminalsayreply stop
```

**************************************************
## **Запуск терминала как сервис с автозагрузкой** 
**************************************************

Запуск -
```
cd ~/
mdmPiTerminal/env/bin/python -u mdmPiTerminal/src/snowboy.py // для запуская сервиса распознования ключевого слова 
mdmPiTerminal/env/bin/python -u mdmPiTerminal/src/sayreply.py // Сервис для ответов от МДМ получение и обработка настроек. 
```
cd ..
chmod +x systemd/service-installer.sh
sudo ./systemd/service-installer.sh

sudo systemctl enable mdmpiterminal.service
sudo systemctl enable mdmpiterminalsayreply.service

sudo systemctl start mdmpiterminal.service
sudo systemctl start mdmpiterminalsayreply.service

```
**************************************************
## **Изменения в МДМ**
**************************************************

В МДМ нужно создать терминал и указать,  что это MajorDroidApi