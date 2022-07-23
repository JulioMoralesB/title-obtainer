##### Libraries required by the main process #####
from asyncio.windows_events import NULL
from hashlib import new
from textwrap import shorten
from tkinter.messagebox import NO
from turtle import clear
import win32gui
import win32process
import psutil
import ctypes

##### Libraries required by the GUI #####

from cgitb import text
from tkinter import Button
import kivy
kivy.require('2.1.0') # replace with your current kivy version !

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.core.window import Window

##### Main process #####

numWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible



def getProcessIDByName(processName):
    processPids = []

    for proc in psutil.process_iter():
        if processName in proc.name():
            processPids.append(proc.pid)

    return processPids

def getHwndsForPid(pid):
    def callback(hwnd, hwnds):
        #if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
        _, foundPid = win32process.GetWindowThreadProcessId(hwnd)

        if foundPid == pid:
            hwnds.append(hwnd)
        return True
    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds 

def getWindowTitleByHandle(hwnd):
    length = GetWindowTextLength(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    GetWindowText(hwnd, buff, length + 1)
    return buff.value

def getWindowHandle(processName):
    pids = getProcessIDByName(processName)

    for i in pids:
        hwnds = getHwndsForPid(i)
        for hwnd in hwnds:
            if IsWindowVisible(hwnd):
                return hwnd

def writeSongName(songName):
    text = u"\u266b " + songName + "                " 
    print(text)
    with open("song.txt", "wb") as file:
        file.write(text.encode("utf8"))
    global currentSong
    currentSong.text = songName
    

def clearSongName():
    with open("song.txt", "w") as file:
        file.write("")
    global currentSong
    currentSong.text = "No song detected"    

def getTitle(obj):
    global windowHandle
    global previousTitle
    windowHandle = getWindowHandle("Spotify.exe")
    windowTitle = getWindowTitleByHandle(windowHandle)
    if windowTitle != NULL and windowTitle != "":
        previousTitle = windowTitle
        writeSongName(previousTitle)
    else:
        print("The selected window was not found")
        previousTitle = ""

def updateTitle(obj):
    global previousTitle
    defaultTitle = "Spotify Premium"
    newTitle = getWindowTitleByHandle(windowHandle)
    if newTitle != previousTitle:
        writeSongName(newTitle)
        previousTitle = newTitle
    if newTitle == defaultTitle:
        newTitle = ""
        clearSongName()



##### GUI using Kivy #####

class MainScreen(FloatLayout):

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)

        self.add_widget(Label(
            text = "Get Song Titles",
            font_size = "50sp",
            color = (.98, .98, 1, 1),
            text_size = (450, None),
            shorten = True,
            shorten_from = "right",
            halign = "center",
            pos_hint = {"center_x": .5, "center_y": .9}
        ))
        self.startButton = Button(
            text = "Start",
            font_size = "25sp",

            background_normal = "",
            background_color = (.12, .84, .38, 1),

            size_hint = (0.2, 0.1),
            pos_hint = {"center_x": .5, "center_y": .7}
        )
        
        self.startButton.bind(on_release = self.start)
        self.add_widget(self.startButton)

        self.stopButton = Button(
            text = "Stop",
            font_size = "25sp",

            background_normal = "",
            background_color = (.85, .06, .25, 1),

            disabled = True,

            size_hint = (0.2, 0.1),
            pos_hint = {"center_x": .5, "center_y": .55}
        )

        self.stopButton.bind(on_release = self.stop)
        self.add_widget(self.stopButton)
        
        self.add_widget(Label(
            text = "Current song:",
            font_size = "30sp",
            color = (.98, .98, 1, 1),
            pos_hint = {"center_x": .5, "center_y": .3}
        ))

        global currentSong
        currentSong = Label(
            text = "No song detected",
            font_size = "30sp",
            color = (.98, .98, 1, 1),

            text_size = (750, None),
            halign = "center",
            padding_y = 100,

            pos_hint = {"center_x": .5, "center_y": .15}
        )

        self.add_widget(currentSong)

    def start(self, obj):
        Clock.schedule_once(getTitle)
        self.scanning = Clock.schedule_interval(updateTitle, 0.1)
        self.stopButton.disabled = False
        self.startButton.disabled = True


    def stop(self, obj):
        clearSongName()
        self.scanning.cancel()
        self.startButton.disabled = False
        self.stopButton.disabled = True

class TitleObtainer(App):

    def build(self):
        self.title = "Title obtainer app"
        self.root = root = MainScreen()
        root.bind(size = self._update_rect, pos=self._update_rect)

        with root.canvas.before:
            Color(0.04, 0.05, 0.06, 1)
            self.rect = Rectangle(size = root.size, pos = root.pos)

            

        Window.bind(on_request_close=self.onClosing)

        Window.size = (800, 450)
        Window.minimum_width, Window.minimum_height = Window.size

        return root

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
        
    def onClosing(self, *args):
        clearSongName()

if __name__ == '__main__':
    TitleObtainer().run()