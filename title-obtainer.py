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

##### Initiating Global variables #####

numWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible


##### GUI using Kivy #####

class MainScreen(FloatLayout):

    ##### Layout initialization #####

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)

        ##### Get Song Titles label ######
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

        ##### Start Button #####
        self.startButton = Button(
            text = "Start",
            font_size = "25sp",

            background_normal = "",
            background_color = (.12, .84, .38, 1),

            size_hint = (0.2, 0.1),
            pos_hint = {"center_x": .5, "center_y": .7}
        )
        
        # If the button is pressed, the main process starts
        self.startButton.bind(on_release = self.start)
        self.add_widget(self.startButton)

        ##### Stop Button #####
        self.stopButton = Button(
            text = "Stop",
            font_size = "25sp",

            background_normal = "",
            background_color = (.85, .06, .25, 1),

            disabled = True,

            size_hint = (0.2, 0.1),
            pos_hint = {"center_x": .5, "center_y": .55}
        )

        #If the button is pressed, the main process stops
        self.stopButton.bind(on_release = self.stop)
        self.add_widget(self.stopButton)
        
        self.add_widget(Label(
            text = "Current song:",
            font_size = "30sp",
            color = (.98, .98, 1, 1),
            pos_hint = {"center_x": .5, "center_y": .3}
        ))

        #Current song label, if no song is detected it displays "No song detected"
        MainScreen.currentSong = Label(
            text = "No song detected",
            font_size = "30sp",
            color = (.98, .98, 1, 1),

            text_size = (750, None),
            halign = "center",
            padding_y = 100,

            pos_hint = {"center_x": .5, "center_y": .15}
        )

        self.add_widget(self.currentSong)

    ##### Main process #####

    ##### Start process #####
    def start(self, obj):
        Clock.schedule_once(self.getTitle) # Detects if the window is open, and if so, it gets its title
        self.scanning = Clock.schedule_interval(self.updateTitle, 0.1) # Updates constantly the window title, with an interval of 0.1 seconds
        self.stopButton.disabled = False # Activates the stop button
        self.startButton.disabled = True # Deactivates the start buttton

    ##### Gets the title and the window handle #####
    def getTitle(self, obj):
        self.windowHandle = self.getWindowHandle("Spotify.exe")
        windowTitle = self.getWindowTitleByHandle(self.windowHandle)
        if windowTitle != NULL and windowTitle != "":
            self.previousTitle = windowTitle
            self.writeSongName(self.previousTitle)
        else:
            print("The selected window was not found")
            self.previousTitle = ""
            MainScreen.udpdateSongName("No window was detected, please, try again")
            self.scanning.cancel()
            self.startButton.disabled = False
            self.stopButton.disabled = True
            
            

    def stop(self, obj):
        self.clearSongName()
        self.scanning.cancel()
        self.startButton.disabled = False
        self.stopButton.disabled = True

    def getProcessIDByName(self, processName):
        processPids = []

        for proc in psutil.process_iter():
            if processName in proc.name():
                processPids.append(proc.pid)

        return processPids

    def getHwndsForPid(self, pid):
        def callback(hwnd, hwnds):
            #if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            _, foundPid = win32process.GetWindowThreadProcessId(hwnd)

            if foundPid == pid:
                hwnds.append(hwnd)
            return True
        hwnds = []
        win32gui.EnumWindows(callback, hwnds)
        return hwnds 

    def getWindowTitleByHandle(self, hwnd):
        length = GetWindowTextLength(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        GetWindowText(hwnd, buff, length + 1)
        return buff.value

    def getWindowHandle(self, processName):
        pids = self.getProcessIDByName(processName)

        for i in pids:
            hwnds = self.getHwndsForPid(i)
            for hwnd in hwnds:
                if IsWindowVisible(hwnd):
                    return hwnd

    def writeSongName(self, songName):
        text = u"\u266b " + songName + "                " 
        print(text)
        
        with open("song.txt", "wb") as file:
            file.write(text.encode("utf8"))

        MainScreen.udpdateSongName(songName)
        

    def clearSongName(self):
        with open("song.txt", "w") as file:
            file.write("")
        MainScreen.udpdateSongName("No song detected")   

    

    def updateTitle(self, obj):
        defaultTitle = "Spotify Premium"
        newTitle = self.getWindowTitleByHandle(self.windowHandle)
        if newTitle != self.previousTitle:
            self.writeSongName(newTitle)
            self.previousTitle = newTitle
        if newTitle == defaultTitle:
            newTitle = ""
            self.clearSongName()
            
    def udpdateSongName(songName):
        MainScreen.currentSong.text = songName

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
        MainScreen.clearSongName(MainScreen)

if __name__ == '__main__':
    TitleObtainer().run()