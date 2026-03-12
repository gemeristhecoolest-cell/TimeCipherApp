from kivy.lang import Builder
from kivy.core.clipboard import Clipboard
from kivy.metrics import dp

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager

from deep_translator import GoogleTranslator
from langdetect import detect

import cipher
import time

KV = """

MDScreenManager:
    LoginScreen:
    MenuScreen:
    EncryptScreen:
    DecryptScreen:


<LoginScreen>

    name: "login"

    MDBoxLayout:
        orientation: "vertical"
        spacing: "20dp"
        padding: "40dp"
        pos_hint: {"center_y": .5}

        MDLabel:
            text: "Cipher App"
            halign: "center"
            font_style: "H4"

        MDTextField:
            id: password
            hint_text: "Enter Password"
            password: True
            size_hint_x: .7
            pos_hint: {"center_x": .5}

        MDRaisedButton:
            text: "Unlock"
            pos_hint: {"center_x": .5}
            on_release: app.check_password(password.text)


<MenuScreen>

    name: "menu"

    MDBoxLayout:
        orientation: "vertical"
        spacing: "30dp"
        padding: "40dp"

        MDLabel:
            text: "Cipher Control"
            halign: "center"
            font_style: "H5"

        MDRaisedButton:
            text: "Encrypt Message"
            pos_hint: {"center_x": .5}
            on_release: app.root.current = "encrypt"

        MDRaisedButton:
            text: "Decrypt Message"
            pos_hint: {"center_x": .5}
            on_release: app.root.current = "decrypt"


<EncryptScreen>

    name: "encrypt"

    MDBoxLayout:
        orientation: "vertical"
        padding: "20dp"
        spacing: "15dp"

        MDTopAppBar:
            title: "Encrypt"
            left_action_items: [["arrow-left", lambda x: app.back_menu()]]

        ScrollView:

            MDTextField:
                id: message
                hint_text: "Enter message"
                multiline: True
                size_hint_y: None
                height: "150dp"
                pos_hint: {"center_x": .5}
                halign: "center"

        MDRaisedButton:
            text: "Encrypt"
            pos_hint: {"center_x": .5}
            on_release: app.encrypt_msg(message.text)

        ScrollView:

            MDLabel:
                id: encrypted
                text: ""
                halign: "center"
                size_hint_y: None
                height: self.texture_size[1]

        MDRaisedButton:
            text: "Copy"
            pos_hint: {"center_x": .5}
            on_release: app.copy_text(encrypted.text)



<DecryptScreen>

    name: "decrypt"

    MDBoxLayout:
        orientation: "vertical"
        padding: "20dp"
        spacing: "15dp"

        MDTopAppBar:
            title: "Decrypt"
            left_action_items: [["arrow-left", lambda x: app.back_menu()]]

        MDRaisedButton:
            text: "Smart Paste"
            pos_hint: {"center_x": .5}
            on_release: app.smart_paste()

        ScrollView:

            MDTextField:
                id: cipher_text
                hint_text: "Cipher text"
                multiline: True
                size_hint_y: None
                height: "120dp"

        MDTextField:
            id: timestamp
            hint_text: "Timestamp"

        MDRaisedButton:
            text: "Decrypt"
            pos_hint: {"center_x": .5}
            on_release: app.decrypt_msg(cipher_text.text, timestamp.text)

        ScrollView:

            MDLabel:
                id: result
                text: ""
                halign: "center"
                size_hint_y: None
                height: self.texture_size[1]
"""


class LoginScreen(MDScreen):
    pass


class MenuScreen(MDScreen):
    pass


class EncryptScreen(MDScreen):
    pass


class DecryptScreen(MDScreen):
    pass


class CipherApp(MDApp):

    password = "1234"

    def build(self):
        return Builder.load_string(KV)

    def check_password(self, text):

        if text == self.password:
            self.root.current = "menu"

    def back_menu(self):
        self.root.current = "menu"

    def translate_to_english(self, text):

        try:
            return GoogleTranslator(source="auto", target="en").translate(text)
        except:
            return text

    def translate_back(self, text, lang):

        try:
            return GoogleTranslator(source="en", target=lang).translate(text)
        except:
            return text

    def encrypt_msg(self, text):

        screen = self.root.get_screen("encrypt")

        try:
            lang = detect(text)
        except:
            lang = "en"

        if lang != "en":
            text = self.translate_to_english(text)

        timestamp = str(int(time.time()))

        encrypted = cipher.encrypt(text, timestamp)

        screen.ids.encrypted.text = f"{encrypted}\n\ntimestamp:{timestamp}"

        self.last_lang = lang

    def decrypt_msg(self, text, timestamp):

        screen = self.root.get_screen("decrypt")

        result = cipher.decrypt(text, timestamp)

        lang = getattr(self, "last_lang", "en")

        if lang != "en":
            result = self.translate_back(result, lang)

        screen.ids.result.text = result

    def copy_text(self, text):

        Clipboard.copy(text)

    def smart_paste(self):

        data = Clipboard.paste()

        screen = self.root.get_screen("decrypt")

        parts = data.split("timestamp:")

        if len(parts) == 2:

            screen.ids.cipher_text.text = parts[0].strip()

            screen.ids.timestamp.text = parts[1].strip()

        else:

            screen.ids.cipher_text.text = data


CipherApp().run()