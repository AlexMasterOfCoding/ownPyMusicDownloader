from __future__ import unicode_literals
import youtube_dl

import datetime

import queue
import threading
import sys


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'downloading':
        print('Downloading - Elapsed: {} mins, ETA: {} mins, Speed: {} kbit/s'.format(d['elapsed'], d['eta'], d['speed']))
    elif d['status'] == 'finished':
        print('Done downloading, now converting ...')
    elif d['status'] == 'error':
        print('An error occured!')

#youtube-dl 
#   --no-playlist [Y]
#   -a "downloads_neu.txt" [N]
#   --console-title [N]
#   -f "bestaudio" [Y]
#   -x  (extract audio only!) [Y]
#   --audio-format "mp3" [Y]
#   --audio-quality "0" [?]
#   --prefer-ffmpeg [Y]
#   --ffmpeg-location "K:\Downloads\Programme\MusikKonverter\ffmpeg-win64\bin" 
#   -o "K:\Musik\Download\%date:~-4%_%date:~3,2%_%date:~0,2%\%%(title)s.%%(ext)s"

now = datetime.datetime.now()
actual_date = now.strftime("%Y_%m_%d")

ydl_opts = {
    'format': 'bestaudio/best',
    'prefer_ffmpeg': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': "K:\Musik\Download\{}\%(title)s.%(ext)s".format(actual_date),
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
    'noplaylist': True,
    'call_home': False,
    'keepvideo': False
}
#with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    #ydl.download(['https://www.youtube.com/watch?v=BaW_jenozKc'])
ydl = youtube_dl.YoutubeDL(ydl_opts)
#ydl.download(['https://www.youtube.com/watch?v=BaW_jenozKc'])

items = ['https://www.youtube.com/watch?v=BaW_jenozKc', 'https://www.youtube.com/watch?v=eM1pA5-XIsk', 'https://www.youtube.com/watch?v=nYz4mqaWWig', 'https://www.youtube.com/watch?v=-1uqn_ry9k4', 'https://www.youtube.com/watch?v=552TojluBKc']

def worker():
    while True:
        download_item = q.get()
        if download_item is None:
            break
        #print(download_item.split(" "))
        ydl.download(download_item.split(" "))
        q.task_done()

q = queue.Queue()
num_worker_threads = 4
threads = []

for i in range(num_worker_threads):
    t = threading.Thread(target=worker)
    t.start()
    threads.append(t)

# use this while program is running and listening on copy of links
for item in items:
    q.put(item)

# block until all tasks are done (only wait if user aborted clipboard listener!)
q.join()

# stop workers (afterwards)
for i in range(num_worker_threads):
    q.put(None)
for t in threads:
    t.join()