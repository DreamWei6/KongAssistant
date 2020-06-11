import snowboydecoder
import sys
import signal
import speech_recognition as sr
import os
from gtts import gTTS
from pygame import mixer
from usb_pixel_ring_v2 import PixelRing
import usb.core
import usb.util
import time
import pyttsx3


interrupted = False
dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)

if dev:
  pixel_ring = PixelRing(dev)
  pixel_ring.trace()


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
    target = r.recognize_google(audio, language="zh-TW")
    print(target)
    pixel_ring.change_pattern(0)

    wordToSound(target)

    pixel_ring.change_pattern('echo')
    pixel_ring.trace()
  except sr.UnknownValueError:
    print("Google Speech Recognition could not understand audio")
    pixel_ring.change_pattern(0)
    wordToSound('我聽不懂')
    pixel_ring.trace()
  except sr.RequestError as e:
    pixel_ring.change_pattern(0)
    print("Could not request results from Google Speech Recognition service; {0}".format(e))
    wordToSound('我出問題了')
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
  engine.setProperty('rate', 180)
  engine.setProperty('voice', 'zh')

  engine.say(text)
  engine.runAndWait()


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


