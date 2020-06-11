import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 180)
engine.setProperty('voice', 'zh')


engine.say("我會說中文")
engine.say("Hello World")
engine.runAndWait()
