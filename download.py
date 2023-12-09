from pytube import YouTube
from pytube import Playlist
from tkinter import *
from tkinter import ttk
import threading

max_file_size = 0

def show_progress_bar(stream=None, chunk=None, bytes_remaining=None):
    global max_file_size    
    if max_file_size == 0:
        pb['value'] = 100
    else:
        percentCount = int((100 - (100*(bytes_remaining/max_file_size))) * 100) / 100
        pb['value'] = percentCount

def single_add():
    global all_playlists
    global max_file_size
    fis_type = file_type.get()
    youtubeObject = YouTube(url_single.get())        
    youtubeObject.register_on_progress_callback(show_progress_bar)
    streams = youtubeObject.streams
    timp = youtubeObject.length
    hh = str(timp//3600)
    mm = str((timp%3600)//60)
    ss = str(timp%60)
    if len(youtubeObject.title) < 90:
        titlu = f"{hh:02}:{mm:02}:{ss:02} --> {youtubeObject.title}"        
    else:
        titlu = f"{hh:02}:{mm:02}:{ss:02} --> {youtubeObject.title[:90] + '...'}"        
    lst.insert(1, titlu)
    if fis_type == 1:        
        stream = streams.get_highest_resolution()        
    else:        
        streams = youtubeObject.streams.filter(only_audio=True)
        stream = streams.first()
    max_file_size = stream.filesize 
    
    try:
        stream.download()
    except:
        pass

def playlist_add():
    global all_playlists    
    playlist = Playlist(url_playlist.get())     
    i = 1   
    for video in playlist.videos:                    
        timp = video.length
        hh = str(timp//3600)
        mm = str((timp%3600)//60)
        ss = str(timp%60)
        if len(video.title) < 90:
            titlu = f"{hh:02}:{mm:02}:{ss:02} --> {video.title}"        
        else:
            titlu = f"{hh:02}:{mm:02}:{ss:02} --> {video.title[:90] + '...'}"
        lst.insert(i, titlu)

    i=1
    fis_type = file_type.get()        
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

window = Tk()
window.geometry('640x500')
window.title('Python Youtube Downloader')
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
Button(window, text='Adauga', command=v_add_t).grid(column=2, row=0)

Label(window, text='Url Playlist: ').grid(column=0, row=1)
url_playlist = Entry(window, width = 80)
url_playlist.grid(column=1, row=1)
Button(window, text='Adauga', command=p_add_t).grid(column=2, row=1)

file_type = IntVar()
file_type.set(1)
Radiobutton(window, text="MP4", variable=file_type, value=1).grid(column=0, row=2, columnspan=1)
Radiobutton(window, text="MP3", variable=file_type, value=2).grid(column=1, row=2, columnspan=1)

Label(window, text='List of Youtube Files').grid(column=0, row=3)

scrollbar = Scrollbar(window, orient="vertical")
scrollbar.grid( column=6, row = 4, sticky=NS )

lst = Listbox(window, width = 100, height=20, yscrollcommand=scrollbar.set)
lst.grid(column=0, row=4, columnspan = 7)

pb = ttk.Progressbar(window, orient = 'horizontal', mode = 'determinate', length=600)
pb.grid(column=0, row=5, columnspan=7)

window.mainloop()