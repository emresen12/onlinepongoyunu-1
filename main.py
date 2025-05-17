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
    def _init_(self, **kwargs):
        super()._init_(**kwargs)
        self.sound = SoundLoader.load("oyununarayüzsesi.mp3")
        if self.sound:
            self.sound.loop = True
            self.sound.volume = 0.3
            self.sound.play()

    def start_pong_game(self):

        import socket
        local_ip = socket.gethostbyname(socket.gethostname())
        subprocess.Popen(["python", "pong_game.py", local_ip, "server"])

    def start_server(self):
        subprocess.Popen(["python", "server.py"])

    def join_online_game(self):
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.textinput import TextInput
        from kivy.uix.button import Button

        layout = BoxLayout(orientation='vertical', spacing=10)
        ip_input = TextInput(hint_text="Enter Server IP", multiline=False)
        btn = Button(text="Connect", size_hint_y=0.3)

        def connect_to_ip(instance):
            ip = ip_input.text
            self.manager.current = "waiting"  # Waiting ekranına geçiş
            popup.dismiss()
            subprocess.Popen(["python", "pong_game.py", ip, "client"])

        btn.bind(on_press=connect_to_ip)
        layout.add_widget(ip_input)
        layout.add_widget(btn)

        popup = Popup(title="Join Game", content=layout, size_hint=(0.8, 0.4))
        popup.open()

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
class WaitingScreen(Screen):
    pass


class PongApp(App):
    def build(self):
        Window.clearcolor = (1, 1, 1, 1)
        sm = ScreenManager()
        sm.add_widget(MainMenu(name="menu"))
        sm.add_widget(HistoryScreen(name="history"))
        sm.add_widget(WaitingScreen(name="waiting"))
        return sm

if __name__=='main_':
   PongApp().run()
