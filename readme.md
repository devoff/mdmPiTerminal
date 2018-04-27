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
nano ~\mdmPiTerminal_git\src\resources\training_service.py
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
cd.. 
nano snowboy.py
```
Теперь нужно отредактировать файл озвучки, указав API yandex 
```
cd ..
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
./systemd/service-installer.sh
```
**************************************************
## **Изменения в МДМ**
**************************************************

что бы работал SayReply нужно отредактировать файл  lib/common.class.php

заменить с 40 по 126 строку на - (не забыв сменить IP адрес МДМ в строчках где есть IP) 
```
/**
 * Summary of sayTo
 * @param mixed $ph        Phrase
 * @param mixed $level     Level (default 0)
 * @param mixed $destination  Destination terminal name
 * @return void
 */
 function sayTo($ph, $level = 0, $destination = '') {
  if (!$destination) {
   return 0;
  }
  $processed=processSubscriptions('SAYTO', array('level' => $level, 'message' => $ph, 'destination' => $destination));
  $terminal_rec=SQLSelectOne("SELECT * FROM terminals WHERE NAME LIKE '".DBSafe($destination)."'");

  if ($terminal_rec['LINKED_OBJECT'] && $terminal_rec['LEVEL_LINKED_PROPERTY']) {
   $min_level=(int)getGlobal($terminal_rec['LINKED_OBJECT'].'.'.$terminal_rec['LEVEL_LINKED_PROPERTY']);
  } else {
   $min_level=(int)getGlobal('minMsgLevel');
  }
   if ($level < $min_level) {
   return 0;
  }
  if ($terminal_rec['MAJORDROID_API'] && $terminal_rec['HOST']) {
      $service_port = '7999';
      $in = 'tts:' . $ph;
      $address = $terminal_rec['HOST'];
      if (!preg_match('/^\d/', $address)) return 0;
      $socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
      if ($socket === false) {
          return 0;
      }
      $result = socket_connect($socket, $address, $service_port);
      if ($result === false) {
          return 0;
      }
      socket_write($socket, $in, strlen($in));
      socket_close($socket);
      return 1;
  } elseif ($terminal_rec['PLAYER_TYPE']=='mpd') {
      $port=$terminal_rec['PLAYER_PORT'];
      $language = SETTINGS_SITE_LANGUAGE;
      if (!$port) {
          $port='8091';
      }
      $host=$terminal_rec['HOST'];
        $filename       = md5($ph) . '_yandex.mp3';
        $cachedVoiceDir = ROOT . 'cached/voice';
        $cachedFileName = $cachedVoiceDir . '/' . $filename;

        $base_url       = 'https://tts.voicetech.yandex.net/generate?key=YANDEX API&text='.urlencode($ph).'&format=mp3&quality=hi&speaker=alyss&emotion=good'; 
        DebMes($base_url);

      if (!file_exists($cachedFileName))
        {

 //          $lang = SETTINGS_SITE_LANGUAGE;
 //          $qs = http_build_query(array('format' => 'mp3', 'lang' => $lang, 'speaker' => $speaker, emotion => $emotion, 'key' => $accessKey, 'text' => $ph));

           try
           {
              $contents = file_get_contents($base_url);
           }
           catch (Exception $e)
           {
              registerError('yandextts', get_class($e) . ', ' . $e->getMessage());
           }
   
           if (isset($contents))
           {
              CreateDir($cachedVoiceDir);
              SaveFile($cachedFileName, $contents);
           }
}


      $md5hash = md5($ph);
//    $url = 'http://'.$host.':'.$port.'/google-home-notifier?language='.$language.'&text='.urlencode($ph);
      $url = 'http://192.168.1.10/popup/app_player.html?ajax=1&play_terminal=mpd&command=refresh&play='.urlencode('http://192.168.1.10/cached/voice/'.$md5hash.'_yandex.mp3');
      getURL($url,0);
      DebMes($url);
      return 1;

  } elseif ($processed) {
   return 1;
  }
  return 0;
 }
 ```
 
 После этого в админке МДМ в разделе терминалы добавить терминал 
 системное имя mpd
 название mpd
 адрес - IP адрес терминала 
 тип плеера MPD 
 порт 6600