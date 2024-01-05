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
import sys
import time

def RemoveSpecialChars(text):
    text = text.capitalize() + ".\n"
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

def ConversieAudio(param):    
    i, chunk, x = param
    r = sr.Recognizer()
    with sr.AudioFile(chunk) as source:
        audio_listened = r.record(source)
        try:
            text = r.recognize_google(audio_listened, language = "ro-RO")                
        except:            
            x[i] = " "
        else:
            text = RemoveSpecialChars(text)                        
            x[i] = text
    return

class YouTubeDownloader:
    def __init__(self):
        self.max_file_size = 0
        self.window = Tk()
        self.window.geometry('640x550')
        self.window.title('Python Youtube Downloader')
        self.window.resizable(False,False)

        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=5)
        self.window.grid_columnconfigure(6, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_rowconfigure(1, weight=1)
        self.window.grid_rowconfigure(2, weight=1)
        self.window.grid_rowconfigure(3, weight=1)
        self.window.grid_rowconfigure(4, weight=1)
        self.window.grid_rowconfigure(5, weight=1)

        self.AddComponents()

    def update_progress(self, x, size):                
        while True:
            total = 0        
            for el in x:
                if len(el) > 0:
                    total += 1
            self.pb['value'] = total * (100 / size)
            pb_val = int(self.pb['value'] * 100) / 100
            self.statusvar.set(f"Recunoastere TEXT: [{total}/{size}] : {pb_val}%")
            if total == size:
                break
            time.sleep(0.1)

    def AddComponents(self):
        Label(self.window, text='Url Video: ').grid(column=0, row=0)
        self.url_single = Entry(self.window, width = 80)
        self.url_single.grid(column=1, row=0)
        Button(self.window, text='Descarca', command=self.v_add_t).grid(column=2, row=0)

        Label(self.window, text='Url Playlist: ').grid(column=0, row=1)
        self.url_playlist = Entry(self.window, width = 80)
        self.url_playlist.grid(column=1, row=1)
        Button(self.window, text='Descarca', command=self.p_add_t).grid(column=2, row=1)

        self.file_type = IntVar()
        self.file_type.set(1)
        Radiobutton(self.window, text="MP4", variable=self.file_type, value=1).grid(column=0, row=2, columnspan=1)
        Radiobutton(self.window, text="MP3", variable=self.file_type, value=2).grid(column=1, row=2, columnspan=1)
        Radiobutton(self.window, text="TXT", variable=self.file_type, value=3).grid(column=2, row=2, columnspan=1)

        Label(self.window, text='List de fisiere:').grid(column=0, row=3)

        self.scrollbar = Scrollbar(self.window, orient="vertical")
        self.scrollbar.grid( column=6, row = 4, sticky=NS )

        self.lst = Listbox(self.window, width = 100, height=20, yscrollcommand=self.scrollbar.set)
        self.lst.grid(column=0, row=4, columnspan = 7)

        self.pb = ttk.Progressbar(self.window, orient = 'horizontal', mode = 'determinate', length=600)
        self.pb.grid(column=0, row=5, columnspan=7)

        self.statusvar = StringVar()
        self.statusvar.set("Pregatit")
        self.sbar = Label(self.window, textvariable=self.statusvar, relief=FLAT, anchor="w", justify="left", width=85)
        self.sbar.grid(column=0, row=6, columnspan=7)

        self.menu_1 = Menu(tearoff=False)
        self.menu_2 = Menu(tearoff=False)
        self.menu_1.add_command(label="Copie", command=self.menu_1_copy)
        self.menu_1.add_command(label="Taie", command=self.menu_1_cut)
        self.menu_1.add_separator()
        self.menu_1.add_command(label="Lipeste", command=self.menu_1_paste)
        self.menu_2.add_command(label="Copie", command=self.menu_2_copy)
        self.menu_2.add_command(label="Taie", command=self.menu_2_cut)
        self.menu_2.add_separator()
        self.menu_2.add_command(label="Lipeste", command=self.menu_2_paste)
        self.url_single.bind('<Button-3>', self.display_popup_1)
        self.url_playlist.bind('<Button-3>', self.display_popup_2)        

    def show_progress_bar(self, stream=None, chunk=None, bytes_remaining=None):
        if self.max_file_size == 0:
            self.pb['value'] = 100
        else:
            percentCount = int((100 - (100*(bytes_remaining/self.max_file_size))) * 100) / 100
            self.pb['value'] = percentCount  

    def DownloadSingleYouTubeObject(self, youtubeObject, fis_type):
        youtubeObject.register_on_progress_callback(self.show_progress_bar)
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
        self.lst.insert(self.lst.size(), item)
        stream = streams.get_highest_resolution()        
        self.max_file_size = stream.filesize  
        self.statusvar.set('Pregatesc video: ... [GATA]')
        start = time.time()
        try:
            self.statusvar.set('Descarc video: ... ')
            stream.download()        
        except:
            pass

        self.statusvar.set('Descarc video: ... [GATA]')
        filepath = stream.default_filename   
        self.pb['value'] = 0

        if fis_type == 2:
            pre, ext = os.path.splitext(filepath)
            output = pre + '.mp3'
            self.statusvar.set('Convertesc la MP3: ... ')
            subprocess.run(["ffmpeg.exe", "-y", "-i", filepath, output], shell=True)
            os.remove(filepath)        
            self.statusvar.set('Convertesc la MP3: ... [GATA]')
        elif fis_type == 3:
            pre, ext = os.path.splitext(filepath)
            output_wav = pre + '.wav'
            output_txt = pre + '.txt'
            self.statusvar.set('Convertesc la WAV: ... ')
            subprocess.run(["ffmpeg.exe", "-y", "-i", filepath, "-acodec", "pcm_s16le", "-ac", "1", "-ar", "16000", output_wav], shell=True)        
            os.remove(filepath)
            self.statusvar.set('Convertesc la WAV: ... [GATA]')
            self.statusvar.set('Pregatesc folder pentru split audio ... ')
            folder_name = "audio-chunks"
            if not os.path.isdir(folder_name):
                os.mkdir(folder_name)
            else:
                for filename in os.listdir('audio-chunks'):
                    if os.path.isfile(os.path.join('audio-chunks', filename)):
                        os.remove(os.path.join('audio-chunks', filename))            
            self.statusvar.set('Pregatesc folder pentru split audio ... [GATA]')
            all_chunks = []                
            self.statusvar.set('Pregatesc fisierul audio pentru recunoastere TEXT ... ')
            sound = AudioSegment.from_wav(output_wav)
            chunks = split_on_silence(sound, min_silence_len=700, silence_thresh=sound.dBFS-14, keep_silence=700)        
            self.statusvar.set('Pregatesc fisierul audio pentru recunoastere TEXT ... [GATA]')
            for i, audio_chunk in enumerate(chunks):
                chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
                audio_chunk.export(chunk_filename, format="wav")
                all_chunks += [chunk_filename]                
                self.pb['value'] += 100 / len(chunks)
                self.pb['value'] = int(self.pb['value'] * 100) / 100
                self.statusvar.set(f"Sparg fisierul mare in bucati mai mici: [{i}/{len(chunks)}] : {self.pb['value']}%")
            print(len(chunks), len(all_chunks))
            time.sleep(10)
            self.pb['value'] = 0            
            with open(output_txt, 'w') as f:
                procs = []            
                x = multiprocessing.Manager().list([[]]*len(chunks))
                params = [(i, all_chunks[i], x) for i in range(len(all_chunks))]                
                threading.Thread(target=self.update_progress, args=(x, len(chunks), )).start()
                with multiprocessing.Pool() as p:
                    p.map(ConversieAudio, params)
                for line in x:
                    f.write(line)

            os.remove(output_wav)
            for filename in os.listdir('audio-chunks'):
                if os.path.isfile(os.path.join('audio-chunks', filename)):
                    os.remove(os.path.join('audio-chunks', filename))   
            os.rmdir('audio-chunks')        
        stop = time.time()
        timp_total = int(stop-start)
        self.statusvar.set(f"Gata! Conversia a durat {timp_total//60} minute si {timp_total%60} secunde")
        self.pb['value'] = 0
        self.window.update()
        self.window.update_idletasks()        

    def single_add(self):
        fis_type = self.file_type.get()
        url = self.url_single.get()
        if len(url) == 0:
            self.statusvar.set("Eroare: Lipseste URL catre video!")
            return
        self.statusvar.set('Pregatesc video: ... ')
        youtubeObject = YouTube(url)  
        try:      
            self.DownloadSingleYouTubeObject(youtubeObject, fis_type)
        except Exception as error:
            self.statusvar.set(f"Eroare: [{error}]")

    def playlist_add(self):
        fis_type = self.file_type.get()        
        playlist = Playlist(self.url_playlist.get())     
        i = 0   
        for video in playlist.videos:        
            try:
                self.DownloadSingleYouTubeObject(video, fis_type)         
            except Exception as error:
                self.statusvar.set(f"Eroare: [{error}]")

    def p_add_t(self):
        threading.Thread(target=self.playlist_add).start()

    def v_add_t(self):
        threading.Thread(target=self.single_add).start()
        
    def display_popup_1(self, event):
        self.menu_1.post(event.x_root, event.y_root)

    def display_popup_2(self, event):
        self.menu_2.post(event.x_root, event.y_root)
        
    def menu_1_copy(self):
        self.url_single.event_generate("<<Copy>>")

    def menu_1_cut(self):
        self.url_single.event_generate("<<Cut>>")

    def menu_1_paste(self):
        self.url_single.event_generate("<<Paste>>")

    def menu_2_copy(self):
        self.url_playlist.event_generate("<<Copy>>")

    def menu_2_cut(self):
        self.url_playlist.event_generate("<<Cut>>")

    def menu_2_paste(self):
        self.url_playlist.event_generate("<<Paste>>")

    def Run(self):
        self.window.mainloop()

def main():
    downloader = YouTubeDownloader()    
    downloader.Run()

if __name__ == "__main__":
    main()     

