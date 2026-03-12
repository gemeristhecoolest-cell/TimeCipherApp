import os
import random
import string
import hashlib
from datetime import datetime

from deep_translator import GoogleTranslator
import pyotp

from kivy.lang import Builder
from kivy.core.clipboard import Clipboard
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog

# ===== LOAD SECRETS FROM FILE =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "password.txt"), "r") as f:
    PASSWORD = f.read().strip()

with open(os.path.join(BASE_DIR, "totp_secret.txt"), "r") as f:
    SECRET_KEY = f.read().strip()

totp = pyotp.TOTP(SECRET_KEY)

# ===== CIPHER FUNCTIONS =====
def seed_from_timestamp(ts):
    h = hashlib.sha256(ts.encode()).hexdigest()
    return int(h, 16)

def generate_cipher(ts):
    random.seed(seed_from_timestamp(ts))
    chars = list(string.printable)
    shuffled = chars[:]
    random.shuffle(shuffled)
    cipher = dict(zip(chars, shuffled))
    decipher = dict(zip(shuffled, chars))
    return cipher, decipher

def translate_once(text):
    try:
        return GoogleTranslator(source="auto", target="en").translate(text)
    except:
        return text

def encrypt(text, ts):
    text = translate_once(text)
    cipher, _ = generate_cipher(ts)
    return "".join(cipher.get(c, c) for c in text)

def decrypt(text, ts):
    _, decipher = generate_cipher(ts)
    return "".join(decipher.get(c, c) for c in text)

# ===== SCREENS =====
class Login(Screen):
    def check_password(self):
        if self.ids.password.text == PASSWORD:
            self.manager.current = "otp"
        else:
            MDDialog(text="Wrong password").open()

class OTP(Screen):
    def verify_code(self):
        code = self.ids.otp.text
        if totp.verify(code):
            self.manager.current = "menu"
        else:
            MDDialog(text="Invalid 2FA code").open()

class Menu(Screen):
    pass

class Cipher(Screen):
    def do_cipher(self):
        text = self.ids.input.text
        ts = datetime.utcnow().strftime("%Y%m%d%H%M")
        result = encrypt(text, ts)
        final = f"{result}\n\ntimestamp:{ts}"
        self.ids.output.text = final

    def copy_output(self):
        Clipboard.copy(self.ids.output.text)

    def back(self):
        self.manager.current = "menu"

class Decipher(Screen):
    def smart_paste(self):
        text = Clipboard.paste()
        if "timestamp:" in text:
            msg, ts = text.split("timestamp:")
            self.ids.input.text = msg.strip()
            self.ids.timestamp.text = ts.strip()
        else:
            self.ids.input.text = text

    def do_decipher(self):
        msg = self.ids.input.text
        ts = self.ids.timestamp.text
        if not ts:
            return
        result = decrypt(msg, ts)
        self.ids.output.text = result

    def back(self):
        self.manager.current = "menu"

# ===== KV LAYOUT =====
KV = '''

ScreenManager:
    Login:
    OTP:
    Menu:
    Cipher:
    Decipher:

<Login>
    name:"login"
    MDBoxLayout:
        orientation:"vertical"
        spacing:dp(20)
        padding:dp(40)

        MDLabel:
            text:"TimeCipher"
            halign:"center"
            font_style:"H4"

        MDTextField:
            id:password
            hint_text:"Password"
            password:True
            mode:"rectangle"
            pos_hint:{"center_x":.5}
            size_hint_x:.8

        MDRaisedButton:
            text:"Enter"
            pos_hint:{"center_x":.5}
            on_release:root.check_password()

<OTP>
    name:"otp"
    MDBoxLayout:
        orientation:"vertical"
        spacing:dp(20)
        padding:dp(40)

        MDLabel:
            text:"Enter 2FA Code"
            halign:"center"
            font_style:"H5"

        MDTextField:
            id:otp
            hint_text:"6-digit code"
            mode:"rectangle"
            pos_hint:{"center_x":.5}
            size_hint_x:.5

        MDRaisedButton:
            text:"Verify"
            pos_hint:{"center_x":.5}
            on_release:root.verify_code()

<Menu>
    name:"menu"
    MDBoxLayout:
        orientation:"vertical"
        spacing:dp(40)
        padding:dp(40)

        MDLabel:
            text:"TimeCipher"
            halign:"center"
            font_style:"H4"

        MDRaisedButton:
            text:"Cipher Message"
            pos_hint:{"center_x":.5}
            on_release:app.root.current="cipher"

        MDRaisedButton:
            text:"Decipher Message"
            pos_hint:{"center_x":.5}
            on_release:app.root.current="decipher"

<Cipher>
    name:"cipher"
    MDBoxLayout:
        orientation:"vertical"
        spacing:dp(15)
        padding:dp(20)

        MDRaisedButton:
            text:"Back"
            pos_hint:{"center_x":.1}
            on_release:root.back()

        MDTextField:
            id:input
            hint_text:"Message"
            multiline:True
            size_hint_y:.3

        MDRaisedButton:
            text:"Cipher"
            pos_hint:{"center_x":.5}
            on_release:root.do_cipher()

        MDTextField:
            id:output
            hint_text:"Encrypted Output"
            multiline:True
            size_hint_y:.3

        MDRaisedButton:
            text:"Copy"
            pos_hint:{"center_x":.5}
            on_release:root.copy_output()

<Decipher>
    name:"decipher"
    MDBoxLayout:
        orientation:"vertical"
        spacing:dp(15)
        padding:dp(20)

        MDRaisedButton:
            text:"Back"
            pos_hint:{"center_x":.1}
            on_release:root.back()

        MDTextField:
            id:input
            hint_text:"Encrypted message"
            multiline:True
            size_hint_y:.3

        MDTextField:
            id:timestamp
            hint_text:"Timestamp"
            size_hint_y:.15

        MDRaisedButton:
            text:"Smart Paste"
            pos_hint:{"center_x":.5}
            on_release:root.smart_paste()

        MDRaisedButton:
            text:"Decipher"
            pos_hint:{"center_x":.5}
            on_release:root.do_decipher()

        MDTextField:
            id:output
            hint_text:"Result"
            multiline:True
            size_hint_y:.3
'''

# ===== APP =====
class TimeCipherApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "BlueGray"
        return Builder.load_string(KV)

if __name__ == "__main__":
    TimeCipherApp().run()            font_style: "H5"

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
