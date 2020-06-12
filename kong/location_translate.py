from googletrans import Translator

#print(googletrans.LANGUAGES)
input = '布吉納法索'
translator = Translator()
result = translator.translate(input, src='zh-tw', dest='en')

print(input)
print(result.text)
