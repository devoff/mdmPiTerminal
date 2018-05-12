# mdmPiTerminal -- Голосовой терминал для MajorDomo
*******************************************************************************************************************************
** Голосовой ассистент для управления умным домом на базе MajorDomo.ru 

** Возможности 
**1. Запуск распознавания по любому ключевому слову (Привет Алиса, проснись дом, Ok Google и тд.)
**2. Передача команды в МДМ
**3. Ответ в терминал через sayReply
**4. Подключение светодиодов (в разработке) 

*************************************************
## **Установка** 
*************************************************
1. Откройте терминал и выполните команды
```
cd ~/
git clone https://github.com/devoff/mdmPiTerminal
cd mdmPiTerminal
chmod +x scripts/mdm-pi-installer.sh
./scripts/mdm-pi-installer.sh
```
Ждем пока установится SnowBoy и все зависимости. 

*************************************************
## **Запись ключевого слова** 
*************************************************

Я бы рекомендовал записать образцы голоса сразу на терминале с тем микрофоном, который будет использоваться, либо записать на сайте snowboy
для этого нужно получиться пройти регистрация на сайте https://snowboy.kitt.ai/ в разделе "Профиль" получить API и прописать его в файле raining_service.py 

```
nano ~/mdmPiTerminal/src/resources/training_service.py
```

Далее нужно записать 3 wav файла, после записи ctrl+c 

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
```
python2 training_service.py 1.wav 2.wav 3.wav alice_privet.pmdl 
````

*************************************************
## **Настройка** 
*************************************************

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

теперь можно попробовать запустить 
```
cd ..
source env/bin/activate # Активируем виртуализацию  питона
python src/snowboy.py
```

**************************************************
## **Запуск терминала как сервис с автозагрузкой** 
**************************************************

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
