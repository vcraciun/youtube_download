import os
import PyPDF3
import pyttsx3
import pdfplumber

file = '12 Rules For Life (Jordan B. Peterson, Norman Doidge etc.) (Z-Library).pdf'
book = open(file, 'rb')
pdfReader = PyPDF3.PdfFileReader(book)

pages = pdfReader.numPages
print(f"Total pagini = {pages}")
finalText = ""
 
with pdfplumber.open(file) as pdf:
    dots = ""
    total_pages = 0
    for i in range(0, pages):        
        dots += '.'
        page = pdf.pages[i]
        text = page.extract_text()
        finalText += text
        if len(dots) == 50:
            print(f"{dots} {total_pages} pages ready")
            dots_100 = ""
            total_pages += 50
    print(f"{dots} {pages} pages ready")
fname, ext = os.path.splitext(file)
with open(fname + '.txt', 'w', encoding="utf-8") as f:
    f.write(finalText)

engine = pyttsx3.init()
voices = engine.getProperty('voices')

for vo in voices:
    print(vo.id)
#engine.setProperty('voice', voices[1].id) 
#engine.setProperty('rate', 150)
#engine.setProperty('volume',.75)

#engine.save_to_file(finalText, '12_rules_for_life.mp3')
#engine.runAndWait()

#engine = pyttsx3.init()
#engine.say(finalText)
#engine.runAndWait()

