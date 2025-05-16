import json
import pygame
import kivy
import subprocess
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.core.audio import SoundLoader

Builder.load_file("interface.kv")

class MainMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sound = SoundLoader.load("oyununarayüzsesi.mp3")
        if self.sound:
            self.sound.loop = True
            self.sound.volume = 0.3
            self.sound.play()

    def start_pong_game(self):
        subprocess.Popen(["python", "pong_game.py"])

    def start_server(self):
        subprocess.Popen(["python", "server.py"])

    def join_online_game(self, server_ip=None):
        # server_ip değişkenini pong_game.py'ye argüman olarak ileteceğiz
        # subprocess çağrısına ekle
        if server_ip:
            subprocess.Popen(["python", "pong_game.py", server_ip])
        else:
            subprocess.Popen(["python", "pong_game.py"])

    def show_all_match(self):
        file="keep_score.json"
        with open(file,"r") as f:
            data=json.load(f)
        history_screen = self.manager.get_screen("history")
        history_screen.ids.player1.text = f"Player 1 wins = {data['player1']}"
        history_screen.ids.player2.text = f"Player 2 wins = {data['player2']}"
        self.manager.current = "history"

class HistoryScreen(Screen):
    def go_back(self):
        self.manager.current ="menu"

class PongApp(App):
    def build(self):
        Window.clearcolor = (1, 1, 1, 1)
        sm = ScreenManager()
        sm.add_widget(MainMenu(name="menu"))
        sm.add_widget(HistoryScreen(name="history"))
        return sm

if __name__=='__main__':
    PongApp().run()
