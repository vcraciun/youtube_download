from deep_translator import MyMemoryTranslator
from deep_translator import GoogleTranslator

data = ""
with open('Slaying the Dragon Within Us_correct.txt', 'r') as f:
    for ln in f.readlines():
        data += ln.strip()

props = data.split('.')
tradus = []
for prop in props:
    print('Traduc: ', prop)
    #trans = MyMemoryTranslator(source="en-US", target="ro-RO").translate(text=prop)
    trans = GoogleTranslator(source='en', target='ro').translate(text=prop)
    tradus += [trans]

with open('Slaying the Dragon Within Us_correct_ro_google.txt', 'w', encoding = 'utf-16le') as f:
    for prop in tradus:
        f.write(prop + '. ')

