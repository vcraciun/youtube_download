import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
from pytube import YouTube
from pytube import Playlist
from tkinter import *
from tkinter import ttk
import multiprocessing
import threading
import subprocess
import os
import time

max_file_size = 0

def show_progress_bar(stream=None, chunk=None, bytes_remaining=None):
    global max_file_size    
    if max_file_size == 0:
        pb['value'] = 100
    else:
        percentCount = int((100 - (100*(bytes_remaining/max_file_size))) * 100) / 100
        pb['value'] = percentCount

def RemoveSpecialChars(text):
    text = f"{text.capitalize()}.\n"
    text = text.replace('\u0102', 'A')                    
    text = text.replace('\u0103', 'a')                    
    text = text.replace('\u0218', 'S')
    text = text.replace('\u015e', 'S')
    text = text.replace('\u0219', 's')
    text = text.replace('\u015f', 's')
    text = text.replace('\u021a', 'T')   
    text = text.replace('\u0162', 'T')                                        
    text = text.replace('\u021b', 't')   
    text = text.replace('\u0163', 't')                       
    text = text.replace('\u00ee', 'i')
    text = text.replace('\u00ce', 'I')
    text = text.replace('\u00c2', 'A')
    text = text.replace('\u00e2', 'a')    
    return text

#ffmpeg -i pentru.mp3 -acodec pcm_s16le -ac 1 -ar 16000 output.wav
def single_add():
    global all_playlists
    global max_file_size
    fis_type = file_type.get()
    url = url_single.get()
    if len(url) == 0:
        statusvar.set("Eroare: Lipseste URL catre video!")
        return
    statusvar.set('Pregatesc video: ... ')
    youtubeObject = YouTube(url)        
    youtubeObject.register_on_progress_callback(show_progress_bar)
    streams = youtubeObject.streams
    timp = youtubeObject.length
    hh = str(timp//3600)
    mm = str((timp%3600)//60)
    ss = str(timp%60)
    if len(youtubeObject.title) < 90:
        titlu = hh+':'+mm+':'+ss+' --> '+youtubeObject.title
    else:
        titlu = hh+':'+mm+':'+ss+' --> '+youtubeObject.title[:90]+'...'
    if fis_type == 1:
        item = "[MP4] : [" + titlu + "]"
    elif fis_type == 2:
        item = "[MP3] : [" + titlu + "]"
    elif fis_type == 3:
        item = "[TXT] : [" + titlu + "]"
    lst.insert(lst.size(), item)
    stream = streams.get_highest_resolution()        
    max_file_size = stream.filesize  
    statusvar.set('Pregatesc video: ... [GATA]')
    start = time.time()
    try:
        statusvar.set('Descarc video: ... ')
        stream.download()        
    except:
        pass

    statusvar.set('Descarc video: ... [GATA]')
    filepath = stream.default_filename   
    pb['value'] = 0

    if fis_type == 2:
        pre, ext = os.path.splitext(filepath)
        output = pre + '.mp3'
        statusvar.set('Convertesc la MP3: ... ')
        subprocess.run(["ffmpeg.exe", "-i", filepath, output], shell=True)
        os.remove(filepath)        
        statusvar.set('Convertesc la MP3: ... [GATA]')
    elif fis_type == 3:
        pre, ext = os.path.splitext(filepath)
        output_wav = pre + '.wav'
        output_txt = pre + '.txt'
        statusvar.set('Convertesc la WAV: ... ')
        subprocess.run(["ffmpeg.exe", "-i", filepath, "-acodec", "pcm_s16le", "-ac", "1", "-ar", "16000", output_wav], shell=True)        
        os.remove(filepath)
        statusvar.set('Convertesc la WAV: ... [GATA]')
        statusvar.set('Pregatesc folder pentru split audio ... ')
        folder_name = "audio-chunks"
        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)
        else:
            for filename in os.listdir('audio-chunks'):
                if os.path.isfile(os.path.join('audio-chunks', filename)):
                    os.remove(os.path.join('audio-chunks', filename))            
        statusvar.set('Pregatesc folder pentru split audio ... [GATA]')
        all_chunks = []                
        statusvar.set('Pregatesc fisierul audio pentru recunoastere TEXT ... ')
        sound = AudioSegment.from_wav(output_wav)
        chunks = split_on_silence(sound, min_silence_len=700, silence_thresh=sound.dBFS-14, keep_silence=700)        
        statusvar.set('Pregatesc fisierul audio pentru recunoastere TEXT ... [GATA]')
        for i, audio_chunk in enumerate(chunks, start=0):
            chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
            audio_chunk.export(chunk_filename, format="wav")
            all_chunks += [chunk_filename]                
            pb['value'] += 100 / len(chunks)
            pb['value'] = int(pb['value'] * 100) / 100
            statusvar.set(f"Sparg fisierul mare in bucati mai mici: [{i}/{len(chunks)}] : {pb['value']}%")
        whole_text = ""
        pb['value'] = 0
        r = sr.Recognizer()
        with open(output_txt, 'w') as f:
            for i, chunk in enumerate(all_chunks):
                with sr.AudioFile(chunk) as source:
                    audio_listened = r.record(source)
                    try:
                        text = r.recognize_google(audio_listened, language = "ro-RO")                
                    except:
                        pb['value'] += 100 / len(all_chunks)
                    else:
                        text = RemoveSpecialChars(text)                        
                        f.write(text)
                        pb['value'] += 100 / len(all_chunks)
                    pb_val = int(pb['value'] * 100) / 100
                    statusvar.set(f"Recunoastere TEXT: [{i}/{len(all_chunks)}] : {pb_val}%")
        os.remove(output_wav)
        for filename in os.listdir('audio-chunks'):
            if os.path.isfile(os.path.join('audio-chunks', filename)):
                os.remove(os.path.join('audio-chunks', filename))   
        os.rmdir('audio-chunks')
    window.update()        
    window.update_idletasks()
    pb['value'] = 0
    stop = time.time()
    timp_total = int(stop-start)
    statusvar.set(f"Gata! Conversia a durat {timp_total//60} minute si {timp_total%60} secunde")
    window.update()        
    window.update_idletasks()

def playlist_add():
    global all_playlists    
    fis_type = file_type.get()        
    playlist = Playlist(url_playlist.get())     
    i = 0   
    for video in playlist.videos:                    
        timp = video.length
        hh = str(timp//3600)
        mm = str((timp%3600)//60)
        ss = str(timp%60)
        if len(video.title) < 90:
            titlu = hh+':'+mm+':'+ss+' --> '+video.title
        else:
            titlu = hh+':'+mm+':'+ss+' --> '+video.title[:90]+'...'

        if fis_type == 1:
            item = f"[MP4] : [{titlu}]"
        elif fis_type == 2:
            item = f"[MP3] : [{titlu}]"
        elif fis_type == 3:
            item = f"[TXT] : [{titlu}]"
        lst.insert(lst.size(), item)
        i += 1

    i=1    
    pb['value'] = 0    
    for video in playlist.videos:                 
        if fis_type == 1:
            stream = video.streams.filter(type='video', progressive=True, file_extension='mp4').order_by('resolution').desc().first()            
        else:
            stream = video.streams.filter(only_audio=True).first()
        stream.download('.')     
        pb['value'] += 100/len(playlist.videos)
        i += 1     
    pb['value'] = 100           

def p_add_t():
    threading.Thread(target=playlist_add).start()

def v_add_t():
    threading.Thread(target=single_add).start()
    
def display_popup_1(event):
    menu_1.post(event.x_root, event.y_root)

def display_popup_2(event):
    menu_2.post(event.x_root, event.y_root)
    
def menu_1_copy():
    url_single.event_generate("<<Copy>>")

def menu_1_cut():
    url_single.event_generate("<<Cut>>")

def menu_1_paste():
    url_single.event_generate("<<Paste>>")

def menu_2_copy():
    url_playlist.event_generate("<<Copy>>")

def menu_2_cut():
    url_playlist.event_generate("<<Cut>>")

def menu_2_paste():
    url_playlist.event_generate("<<Paste>>")

window = Tk()
window.geometry('640x550')
window.title('Python Youtube Downloader')
window.resizable(False,False)
window.grid_columnconfigure(0, weight=1)
window.grid_columnconfigure(1, weight=5)
window.grid_columnconfigure(6, weight=1)
window.grid_rowconfigure(0, weight=1)
window.grid_rowconfigure(1, weight=1)
window.grid_rowconfigure(2, weight=1)
window.grid_rowconfigure(3, weight=1)
window.grid_rowconfigure(4, weight=1)
window.grid_rowconfigure(5, weight=1)

Label(window, text='Url Video: ').grid(column=0, row=0)
url_single = Entry(window, width = 80)
url_single.grid(column=1, row=0)
Button(window, text='Descarca', command=v_add_t).grid(column=2, row=0)

Label(window, text='Url Playlist: ').grid(column=0, row=1)
url_playlist = Entry(window, width = 80)
url_playlist.grid(column=1, row=1)
Button(window, text='Descarca', command=p_add_t).grid(column=2, row=1)

file_type = IntVar()
file_type.set(1)
Radiobutton(window, text="MP4", variable=file_type, value=1).grid(column=0, row=2, columnspan=1)
Radiobutton(window, text="MP3", variable=file_type, value=2).grid(column=1, row=2, columnspan=1)
Radiobutton(window, text="TXT", variable=file_type, value=3).grid(column=2, row=2, columnspan=1)

Label(window, text='List de fisiere:').grid(column=0, row=3)

scrollbar = Scrollbar(window, orient="vertical")
scrollbar.grid( column=6, row = 4, sticky=NS )

lst = Listbox(window, width = 100, height=20, yscrollcommand=scrollbar.set)
lst.grid(column=0, row=4, columnspan = 7)

pb = ttk.Progressbar(window, orient = 'horizontal', mode = 'determinate', length=600)
pb.grid(column=0, row=5, columnspan=7)

statusvar = StringVar()
statusvar.set("Pregatit")
sbar = Label(window, textvariable=statusvar, relief=FLAT, anchor="w", justify="left", width=85)
sbar.grid(column=0, row=6, columnspan=7)

menu_1 = Menu(tearoff=False)
menu_2 = Menu(tearoff=False)
menu_1.add_command(label="Copie", command=menu_1_copy)
menu_1.add_command(label="Taie", command=menu_1_cut)
menu_1.add_separator()
menu_1.add_command(label="Lipeste", command=menu_1_paste)
menu_2.add_command(label="Copie", command=menu_2_copy)
menu_2.add_command(label="Taie", command=menu_2_cut)
menu_2.add_separator()
menu_2.add_command(label="Lipeste", command=menu_2_paste)
url_single.bind('<Button-3>', display_popup_1)
url_playlist.bind('<Button-3>', display_popup_2)

window.mainloop()
