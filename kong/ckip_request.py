import json
import requests
import sys

url = 'https://ckip.iis.sinica.edu.tw/api/corenlp/?ner&ws'

input = sys.argv[1]

header = {
  'Content-Type': 'application/json; charset=utf8'
}

payload = {
  'text': input
}

r = requests.post(url, data=json.dumps(payload), headers = header)
print(r.json())
datas = r.json()['ner'][0]

for data in datas:
  print(data)

datas = r.json()['ws'][0]

for data in datas:
  print(data)
#  if data['ner'] == 'GPE':
#    print(data['text'])
