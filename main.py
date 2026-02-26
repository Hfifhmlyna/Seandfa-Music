from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel

class SeandfaMobile(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Brown"
        screen = MDScreen()
        
        screen.add_widget(MDLabel(
            text="SEANDFA MOBILE ☕", 
            halign="center", 
            pos_hint={"center_y": 0.7},
            font_style="H4"
        ))
        
        screen.add_widget(MDRaisedButton(
            text="COBA PUTAR MUSIK",
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        ))
        return screen

if __name__ == "__main__":
    SeandfaMobile().run()
