import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
from pytubefix import YouTube
from pytubefix import Playlist
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import multiprocessing
import threading
import subprocess
import os
import sys
import time
import json
import logging

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
    i, chunk, x, lang = param
    r = sr.Recognizer()
    with sr.AudioFile(chunk) as source:
        audio_listened = r.record(source)
        try:
            #text = r.recognize_google(audio_listened, language = "ro-RO")                
            #text = r.recognize_google(audio_listened, language = "en-EN")
            text = r.recognize_google(audio_listened, language = lang)
        except:            
            x[i] = ""
        else:
            text = RemoveSpecialChars(text)                        
            x[i] = text
    return

class YouTubeDownloader:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.max_file_size = 0
        self.window = Tk()
        self.window.geometry('640x640')
        self.window.title('Python Youtube Downloader')
        self.window.resizable(False,False)
        self.min_tresh = 15
        self.max_tresh = 60

        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=5)
        self.window.grid_columnconfigure(6, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_rowconfigure(1, weight=1)
        self.window.grid_rowconfigure(2, weight=1)
        self.window.grid_rowconfigure(3, weight=1)
        self.window.grid_rowconfigure(4, weight=1)
        self.window.grid_rowconfigure(5, weight=1)
        self.window.grid_rowconfigure(6, weight=1)
        self.window.grid_rowconfigure(7, weight=1)
        self.window.grid_rowconfigure(8, weight=1)
        self.window.grid_rowconfigure(9, weight=1)
        self.window.grid_rowconfigure(10, weight=1)

        self.AddComponents()

    def update_progress(self, x, size):                
        while True:
            total = 0        
            for el in x:
                if len(el) > 0:
                    total += 1
            try:
                self.pb['value'] = total * (100 / size)
            except:
                pass
            pb_val = int(self.pb['value'] * 100) / 100
            try:
                self.statusvar.set(f"Recunoastere TEXT: [{total}/{size}] : {pb_val}%")
            except:
                pass
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

        Label(self.window, text='Fisier audio: ').grid(column=0, row=2)
        self.audio_file = Entry(self.window, width = 80)
        self.audio_file.grid(column=1, row=2)
        Button(self.window, text='Cauta', command=self.f_add_t).grid(column=2, row=2)
        
        Label(self.window, text='Folder audio: ').grid(column=0, row=3)
        self.audio_folder = Entry(self.window, width = 80)
        self.audio_folder.grid(column=1, row=3)
        Button(self.window, text='Transforma', command=self.d_add_t).grid(column=2, row=3)        

        self.file_type = IntVar()
        self.file_type.set(1)
        Radiobutton(self.window, text="MP4", variable=self.file_type, value=1).grid(column=0, row=4, columnspan=1)
        Radiobutton(self.window, text="MP3", variable=self.file_type, value=2).grid(column=1, row=4, columnspan=1)
        Radiobutton(self.window, text="TXT", variable=self.file_type, value=3).grid(column=2, row=4, columnspan=1)

        self.language = IntVar()
        self.language.set(1)
        Radiobutton(self.window, text="RO", variable=self.language, value=1).grid(column=0, row=5, columnspan=1)
        Radiobutton(self.window, text="EN", variable=self.language, value=2).grid(column=2, row=5, columnspan=1)

        Label(self.window, text='List de fisiere:').grid(column=0, row=6)

        self.scrollbar = Scrollbar(self.window, orient="vertical")
        self.scrollbar.grid( column=6, row = 7, sticky=NS )

        self.lst = Listbox(self.window, width = 100, height=20, yscrollcommand=self.scrollbar.set)
        self.lst.grid(column=0, row=7, columnspan = 8)

        self.pb = ttk.Progressbar(self.window, orient = 'horizontal', mode = 'determinate', length=600)
        self.pb.grid(column=0, row=8, columnspan=8)

        self.pb2 = ttk.Progressbar(self.window, orient = 'horizontal', mode = 'determinate', length=600)
        self.pb2.grid(column=0, row=9, columnspan=8)

        self.pb['value'] = 0
        self.pb2['value'] = 0

        self.statusvar = StringVar()
        self.statusvar.set("Pregatit")
        self.sbar = Label(self.window, textvariable=self.statusvar, relief=FLAT, anchor="w", justify="left", width=85)
        self.sbar.grid(column=0, row=10, columnspan=7)

        self.menu_1 = Menu(tearoff=False)
        self.menu_2 = Menu(tearoff=False)
        self.menu_3 = Menu(tearoff=False)
        self.menu_4 = Menu(tearoff=False)
        
        self.menu_1.add_command(label="Copie", command=self.menu_copy_1)
        self.menu_1.add_command(label="Taie", command=self.menu_cut_1)
        self.menu_1.add_separator()
        self.menu_1.add_command(label="Lipeste", command=self.menu_paste_1)
        
        self.menu_2.add_command(label="Copie", command=self.menu_copy_2)
        self.menu_2.add_command(label="Taie", command=self.menu_cut_2)
        self.menu_2.add_separator()
        self.menu_2.add_command(label="Lipeste", command=self.menu_paste_2)

        self.menu_3.add_command(label="Copie", command=self.menu_copy_3)
        self.menu_3.add_command(label="Taie", command=self.menu_cut_3)
        self.menu_3.add_separator()
        self.menu_3.add_command(label="Lipeste", command=self.menu_paste_3)        

        self.menu_4.add_command(label="Copie", command=self.menu_copy_4)
        self.menu_4.add_command(label="Taie", command=self.menu_cut_4)
        self.menu_4.add_separator()
        self.menu_4.add_command(label="Lipeste", command=self.menu_paste_4)        
        
        self.url_single.bind('<Button-3>', self.display_popup_1)
        self.url_playlist.bind('<Button-3>', self.display_popup_2)  
        self.audio_file.bind('<Button-3>', self.display_popup_3)  
        self.audio_folder.bind('<Button-3>', self.display_popup_4)  
        

    def show_progress_bar(self, stream=None, chunk=None, bytes_remaining=None):
        if self.max_file_size == 0:
            self.pb['value'] = 100
        else:
            percentCount = int((100 - (100*(bytes_remaining/self.max_file_size))) * 100) / 100
            self.pb['value'] = percentCount  

    def ConvertToWAV(self, filepath, output_wav):
        self.statusvar.set('Convertesc la WAV: ... ')
        subprocess.run(["ffmpeg.exe", "-y", "-i", filepath, "-acodec", "pcm_s16le", "-ac", "1", "-ar", "16000", output_wav], shell=True)        
        self.statusvar.set('Convertesc la WAV: ... [GATA]')

    def ClearChunksFolder(self, folder_name):
        for filename in os.listdir(folder_name):
            if os.path.isfile(os.path.join(folder_name, filename)):
                os.remove(os.path.join(folder_name, filename))     

    def PrepareFolder(self, folder_name):
        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)
        else:
            self.ClearChunksFolder("audio-chunks")

    def EraseChunksFolder(self, folder_name):
        try:
            self.ClearChunksFolder(folder_name)
            os.remove(folder_name)        
        except:
            pass

    def SplitToChunks(self, chunks, folder_name):
        all_chunks = []                
        for i, audio_chunk in enumerate(chunks):
            chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
            audio_chunk.export(chunk_filename, format="wav")
            all_chunks += [chunk_filename]                
            self.pb['value'] += 100 / len(chunks)
            self.pb['value'] = int(self.pb['value'] * 100) / 100
            self.statusvar.set(f"Sparg fisierul mare in bucati mai mici: [{i}/{len(chunks)}] : {self.pb['value']}%")
        self.statusvar.set(f"Sparg fisierul mare in bucati mai mici: [{len(chunks)}/{len(chunks)}] : {100}%")
        return all_chunks
    
    def ConvertChunksToText(self, chunks, all_chunks):
        procs = []        
        self.pb['value'] = 0            
        x = multiprocessing.Manager().list([[]]*len(chunks))
        lang = "ro-RO" if self.language.get() == 1 else "en-EN"
        params = [(i, all_chunks[i], x, lang) for i in range(len(all_chunks))]                
        with multiprocessing.Pool() as p:
            p.map(ConversieAudio, params)
        return x
    
    def ConvertToMP3(self, filepath, output):
        self.statusvar.set('Convertesc la MP3: ... ')
        subprocess.run(["ffmpeg.exe", "-y", "-i", filepath, output], shell=True)
        os.remove(filepath)        
        self.statusvar.set('Convertesc la MP3: ... [GATA]')

    def DownloadSingleYouTubeObject(self, youtubeObject, fis_type, url):
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

        if fis_type == 1:
            self.pb2['value'] = 100
        if fis_type == 2:
            pre, ext = os.path.splitext(filepath)
            output = pre + '.mp3'
            self.pb2['value'] = 50
            self.ConvertToMP3(filepath, output)
            self.pb2['value'] = 100
        elif fis_type == 3:
            self.PrepareFolder("audio-chunks")
            pre, ext = os.path.splitext(filepath)
            output = pre + '.mp3'
            output_txt = pre + '.txt'
            self.ConvertToMP3(filepath, output)
            self.TransformMP3ToText(output, url) 
            self.EraseChunksFolder('audio-chunks')       

        stop = time.time()
        timp_total = int(stop-start)
        self.statusvar.set(f"Gata! Conversia a durat {timp_total//60} minute si {timp_total%60} secunde")
        self.pb['value'] = 0
        self.window.update()
        self.window.update_idletasks()

    def GetAudioSegmentFromExt(self, fname, ext):
        self.statusvar.set('Pregatesc fisierul audio pentru recunoastere TEXT ... ')
        if ext == '.mp3':
            sound = AudioSegment.from_mp3(fname)
        else:
            sound = AudioSegment.from_wav(fname)        
        return sound
    
    def CountWords(self, x):
        words = 0                
        for item in x:
            if len(item) == 0:
                continue
            item = item.strip()
            if len(item) == 0:
                continue
            words += len(item.split(' '))    
        return words
    
    def ComputeIteration(self, i, sound):
        tresh = i * (-1)
        self.ClearChunksFolder('audio-chunks')
        chunks = split_on_silence(sound, min_silence_len=1000, silence_thresh=tresh, keep_silence=700, seek_step=100)        
        all_chunks = self.SplitToChunks(chunks, folder_name="audio-chunks")             
        x = self.ConvertChunksToText(chunks, all_chunks)
        self.statusvar.set(f'Conversie AUDIO la TEXT: S-a terminat varianta [{i}] -> {len(x)} cuvinte')
        if len(x) == 0:
            return []
        words = self.CountWords(x)
        self.best_config[words] = (i, x)
        self.logger.info(f"Cuurent iteration: ({i}:{words})")
        return x
    
    def BinarySearch(self, min, max, lmin, lmax, cuvinte_1, cuvinte_n, sound):
        cuvinte3 = self.ComputeIteration((min+max)//2, sound)
        l3 = self.CountWords(cuvinte3)
        if lmax < l3 and l3 > lmin:
            if (min+max)//2 + 1 == max:
                return cuvinte3
            else:
                return self.BinarySearch((min+max)//2, max, l3, lmax, cuvinte3, cuvinte_n, sound)
        else:
            if lmax > l3:
                self.logger.info(f'Eroare --> trebuie extins range-ul: {min}:{lmin}, {(min+max)//2}:{l3}, {max}:{lmax}')
            else:
                if l3 > lmin:
                    if (min+max)//2 == min + 1:
                        return cuvinte3
                    else:
                        return self.BinarySearch((min+max)//2, max, l3, lmax, cuvinte3, cuvinte_n, sound)
                else:
                    if (min+max)//2 == min + 1:
                        return cuvinte_1
                    else:
                        return self.BinarySearch(min, (min+max)//2, lmin, l3, cuvinte_1, cuvinte3, sound)
        return []
    
    def FindSolutions(self, sound):
        self.statusvar.set('Caut solutia cea mai buna de conversie, s-ar putea sa dureze cateva minute ... ')
        self.pb['value'] = 0      
        self.pb2['value'] = 0              
        self.best_config={}
        cuvinte_1 = self.ComputeIteration(self.min_tresh, sound)        
        cuvinte_n = self.ComputeIteration(self.max_tresh, sound)
        self.BinarySearch(self.min_tresh, self.max_tresh, self.CountWords(cuvinte_1), self.CountWords(cuvinte_n), cuvinte_1, cuvinte_n, sound)
        solutii_sortat = dict(reversed(sorted(self.best_config.items())))
        return solutii_sortat
    
    def ScrieTextRezultat(self, solutie, output_txt):
        first_key = next(iter(solutie))
        value = solutie[first_key]
        with open(output_txt, 'w') as f:
            for line in value[1]:
                f.write(line)

    def ScrieStatistica(self, solutie, fname):
        if os.path.exists('statistica.json'):
            data = json.load(open('statistica.json', 'r'))
        else:
            data = {}
        data[fname] = [{v[0]: k} for _, (k,v) in enumerate(solutie.items()) ]
        json.dump(data, open('statistica.json', 'w'))

    def TransformMP3ToText(self, fname, url):
        self.PrepareFolder('audio-chunks')        
        pre, ext = os.path.splitext(fname)
        output_txt = pre + '.txt'
        start = time.time()
        sound = self.GetAudioSegmentFromExt(fname, ext)        
        solutie = self.FindSolutions(sound)        
        self.ScrieTextRezultat(solutie, output_txt)
        if len(url) == 0:
            self.ScrieStatistica(solutie, fname)
        else:
            self.ScrieStatistica(solutie, url)
        
    def mp3_process(self, fname):        
        fis_type = self.file_type.get()
        if fis_type != 3:
            self.statusvar.set(f"EROARE: TRebuie sa bifati optiunea TXT pentru conversie!")
            return        
        if len(fname) == 0:
            self.statusvar.set("EROARE: Numele de fisier lipseste!")
            return        
        start = time.time()
        self.lst.insert(self.lst.size(), fname)
        self.TransformMP3ToText(fname, "")    
        self.EraseChunksFolder('audio-chunks')
        stop = time.time()
        timp_total = int(stop-start)
        self.statusvar.set(f"Gata! Conversia a durat {timp_total//60} minute si {timp_total%60} secunde")
        self.pb['value'] = 0
        self.window.update()
        self.window.update_idletasks() 
        
        
    def file_add(self):        
        fname = filedialog.askopenfilename(initialdir = "./", title = "Selectati fisier Audio", filetypes = (("Fisiere MP3", "*.mp3*"), ("Fisiere WAV", "*.wav"), ("Toate fisierele", "*.*")))
        self.audio_file.delete(0, END)
        self.audio_file.insert(0, fname)
        self.mp3_process(fname)

    def folder_add(self):
        folder = self.audio_folder.get()
        file_list = [f for f in os.listdir(folder) if f.endswith('.mp3')]
        for mp3 in file_list:
            self.mp3_process(f"{folder}\\{mp3}")

    def single_add(self):
        fis_type = self.file_type.get()
        url = self.url_single.get()
        if len(url) == 0:
            self.statusvar.set("Eroare: Lipseste URL catre video!")
            return
        self.statusvar.set('Pregatesc video: ... ')
        youtubeObject = YouTube(url)  
        try:      
            self.DownloadSingleYouTubeObject(youtubeObject, fis_type, url)
        except Exception as error:
            self.statusvar.set(f"Eroare: [{error}]")

    def playlist_add(self):
        fis_type = self.file_type.get()        
        playlist = Playlist(self.url_playlist.get())     
        i = 0   
        for video in playlist.videos:
            try:
                self.DownloadSingleYouTubeObject(video, fis_type, video.watch_url)         
            except Exception as error:
                self.statusvar.set(f"Eroare: [{error}]")

    def p_add_t(self):
        threading.Thread(target=self.playlist_add).start()

    def v_add_t(self):
        threading.Thread(target=self.single_add).start()

    def f_add_t(self):
        threading.Thread(target=self.file_add).start()
        
    def d_add_t(self):
        threading.Thread(target=self.folder_add).start()
      
    def display_popup_1(self, event):
        self.menu_1.post(event.x_root, event.y_root)
    def display_popup_2(self, event):
        self.menu_2.post(event.x_root, event.y_root)
    def display_popup_3(self, event):
        self.menu_3.post(event.x_root, event.y_root)
    def display_popup_4(self, event):
        self.menu_4.post(event.x_root, event.y_root)        
        
    def menu_copy_1(self):
        self.url_single.event_generate("<<Copy>>")
    def menu_cut_1(self):
        self.url_single.event_generate("<<Cut>>")
    def menu_paste_1(self):
        self.url_single.event_generate("<<Paste>>")
    def menu_copy_2(self):
        self.url_playlis.event_generate("<<Copy>>")
    def menu_cut_2(self):
        self.url_playlis.event_generate("<<Cut>>")
    def menu_paste_2(self):
        self.url_playlis.event_generate("<<Paste>>")
    def menu_copy_3(self):
        self.audio_file.event_generate("<<Copy>>")
    def menu_cut_3(self):
        self.audio_file.event_generate("<<Cut>>")
    def menu_paste_3(self):
        self.audio_file.event_generate("<<Paste>>")
    def menu_copy_4(self):
        self.audio_folder.event_generate("<<Copy>>")
    def menu_cut_4(self):
        self.audio_folder.event_generate("<<Cut>>")
    def menu_paste_4(self):
        self.audio_folder.event_generate("<<Paste>>")        

    def Run(self):
        self.window.mainloop()

def main():
    logging.basicConfig(filename='Youtube-Downloader.log', level=logging.INFO)    
    downloader = YouTubeDownloader()    
    downloader.Run()

if __name__ == "__main__":
    main()     

