#!/usr/bin/python3
# # -*- coding: utf-8 -*-

from __future__ import unicode_literals

import time
import threading

import pyperclip

import youtube_dl

import datetime

import queue
import sys

base_path = "C:\\Users\\Alex\\Music"

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
    else:
        print('Unknown status:', d,  d['status'])

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
    'outtmpl': "{}\Download\{}\%(title)s.%(ext)s".format(base_path, actual_date),
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
    'noplaylist': True,
    'call_home': False,
    'keepvideo': False
}

ydl = youtube_dl.YoutubeDL(ydl_opts)

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

#https://www.youtube.com/watch?v=j99wM1_eXPs
YT_BASE_URL = "www.youtube.com"

#https://youtu.be/k9PhnYUhCaE
YT_SHORT_URL = "youtu.be"

def is_url_and_yt(url):
    if url.startswith("https://") and (YT_BASE_URL in url or YT_SHORT_URL in url):
        return True
    return False

def download_url(clipboard_content):
    print("Found Youtube URL: %s" % str(clipboard_content))
    q.put(clipboard_content)

class ClipboardWatcher(threading.Thread):
    def __init__(self, predicate, callback, pause=5.):
        super(ClipboardWatcher, self).__init__()
        self._predicate = predicate
        self._callback = callback
        self._pause = pause
        self._stopping = False

    def run(self):       
        recent_value = ""
        while not self._stopping:
            tmp_value = pyperclip.paste()
            if tmp_value != recent_value:
                recent_value = tmp_value
                if self._predicate(recent_value):
                    self._callback(recent_value)
            time.sleep(self._pause)

    def stop(self):
        self._stopping = True

def main():
    print("Started Youtube-Clipboard listener for YT Downloads...")
    watcher = ClipboardWatcher(is_url_and_yt, 
                               download_url,
                               1.)
    watcher.start()
    while True:
        try:
            #print("Waiting for changed clipboard...")
            time.sleep(10)
        except KeyboardInterrupt:
            print("Stopping Youtube-Clipboard listener and going to join threads ...")
            watcher.stop()
            # block until all tasks are done (only wait if user aborted clipboard listener!)
            # Maybe blocking if error occurs?
            print("Joining Queue...")
            q.join()

            # stop workers (afterwards)
            print("Stopping workers...")
            for i in range(num_worker_threads):
                q.put(None)
            print("Joining Threads...")
            for t in threads:
                t.join()
            print("Bye!")
            sys.exit()
            quit()
        except:
            print("Unexpected error:", sys.exc_info()[0])
            for t in threads:
                t.join()
            sys.exit()
            quit()

if __name__ == "__main__":
    main()