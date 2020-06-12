import snowboydecoder
import sys
import signal
import speech_recognition as sr
import os
#from gtts import gTTS
#from pygame import mixer
from usb_pixel_ring_v2 import PixelRing
import usb.core
import usb.util
import time
import pyttsx3
import json
import requests
from googletrans import Translator
import pyowm
from Keys import open_weather_api
from myweather import weather_status

interrupted = False
dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)

# Initialization Setting
if dev:
  pixel_ring = PixelRing(dev)
  pixel_ring.trace()

ckip_url = 'https://ckip.iis.sinica.edu.tw/api/corenlp/?ner'
header = {
  'Content-Type': 'application/json; charset=utf8'
}
payload = {
  'text': ' '
}

owm = pyowm.OWM(open_weather_api)

# Function
def audioRecorderCallback(fname):
  pixel_ring.think()
  print("converting audio to text")
  r = sr.Recognizer()
  with sr.AudioFile(fname) as source:
    audio = r.record(source, duration=3)  # read the entire audio file
  # recognize speech using Google Speech Recognition
  try:
    # for testing purposes, we're just using the default API key
    # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
    # instead of `r.recognize_google(audio)`
    echo = r.recognize_google(audio, language="zh-TW")
    print(echo)

    word_break = ckip(echo)
    skill = check_skill(word_break)


    pixel_ring.change_pattern(0)
    if skill == None:
      wordToSound(echo)
      print(f"Skill : {skill}")
    else:
      if skill['skill'] == 'weather':
        print(f"Skill : {skill['skill']}")
        echo = f"{skill['location']}現在的天氣為{skill['status']} , 溫度{skill['temp']}度"
        print(echo)
        wordToSound(echo)

    pixel_ring.change_pattern('echo')
    pixel_ring.trace()
  except sr.UnknownValueError:
    print("Google Speech Recognition could not understand audio")
    pixel_ring.change_pattern(0)
    wordToSound('我聽不懂')
    pixel_ring.change_pattern('echo')
    pixel_ring.trace()
  except sr.RequestError as e:
    pixel_ring.change_pattern(0)
    print("Could not request results from Google Speech Recognition service; {0}".format(e))
    wordToSound('我好像沒連上WiFi')
    pixel_ring.change_pattern('echo')
    pixel_ring.trace()

  os.remove(fname)


def detectedCallback():
  pixel_ring.spin()
  print('recording audio...', end='', flush=True)

def signal_handler(signal, frame):
  global interrupted
  interrupted = True


def interrupt_callback():
  global interrupted
  return interrupted

'''
def wordToSound(text):
  file_name = 'w2s.mp3'
  tts = gTTS(text, lang='zh-TW')
  tts.save(file_name)

  mixer.init()
  mixer.music.load(file_name)
  mixer.music.play()
  while mixer.music.get_busy() == True:
    continue
  mixer.music.stop()
  mixer.quit()
'''

def wordToSound(text):
  engine = pyttsx3.init()
  engine.setProperty('rate', 200)
  engine.setProperty('voice', 'zh')

  engine.say(text)
  engine.runAndWait()

def ckip(text):
  payload['text'] = text
  r = requests.post(ckip_url, data=json.dumps(payload), headers = header)
  #print(f"Word Break Complite \n{r.json()['ner'][0]}")
  return r.json()['ner'][0]

def check_skill(response):
  ner, text = parse(response)
  #print(f"Check \nNer : {ner}\nText : {text}\n")
  if 'GPE' in ner and ner.count('GPE') == 1:
    for i in range(len(ner)):
      if ner[i] == None:
        if text[i].find('天氣') != -1:
          tmp = {'skill': 'weather'}
          print(f"{'Skill': <15} : {tmp['skill']: >12}")
          tmp['location'] = text[ner.index('GPE')]
          lengh = 12 - len(tmp['location'])
          print(f"{'Location(zh)': <15} : {tmp['location']: >{lengh}}")
          location_en = to_english(tmp['location'])
          print(f"{'Location(en)': <15} : {location_en: >12}")
          weather = get_weather(location_en)
          if weather == None:
            print("API Request Failed")
            return None
          else:
            tmp['temp']   = weather[0]
            tmp['status'] = weather[1]
            print(f"{'Temp': <15} : {tmp['temp']: >12}")
            length = 12 - len(tmp['status'])
            print(f"{'Status': <15} : {tmp['status']: >{length}}")
            return tmp
    return None
  else:
    return None

def to_english(text):
  translator = Translator()
  result = translator.translate(text, src = 'zh-tw', dest = 'en')
  return result.text

def get_weather(location):
  try:
    observation = owm.weather_at_place(location)
    w = observation.get_weather()
    temp = w.get_temperature('celsius')
    status = w.get_detailed_status()
  except:
    return None
  return [int(temp['temp']), weather_status[status]]

def parse(res):
  ner = []
  text = []
  for r in res:
    ner.append(r['ner'])
    text.append(r['text'])
  #print(f"Parse Complite\nNer : {ner}\nText : {text}\n")
  return ner, text

# main
def main():
  if len(sys.argv) == 1:
    print("Error: need to specify model name")
    print("Usage: python demo.py your.model")
    sys.exit(-1)

  model = sys.argv[1]

  # capture SIGINT signal, e.g., Ctrl+C
  signal.signal(signal.SIGINT, signal_handler)
  detector = snowboydecoder.HotwordDetector(model, sensitivity=0.38)
  print('Listening... Press Ctrl+C to exit')

  # main loop
  detector.start(detected_callback=detectedCallback,
                 audio_recorder_callback=audioRecorderCallback,
                 interrupt_check=interrupt_callback,
                 sleep_time=0.01)

  detector.terminate()

if __name__ == '__main__':
  main()


