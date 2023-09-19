import socket
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.core.window import Window

class ChatClientApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', spacing=10)

        self.nickname_input = TextInput(hint_text='Enter your nickname', size_hint=(None, None), size=(300, 30), multiline=False)
        self.nickname_input.bind(on_text_validate=self.join_chat)
        self.layout.add_widget(Label())  # Spacer
        self.layout.add_widget(self.nickname_input)
        self.layout.add_widget(Label())  # Spacer

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        return self.layout

    def join_chat(self, instance):
        self.nickname = self.nickname_input.text
        self.layout.clear_widgets()  # Remove the nickname input

        # Make the "Type your message" input smaller
        self.message_input = TextInput(hint_text='Type your message', size_hint_y=None, height=30, multiline=False)
        self.message_input.bind(on_text_validate=self.send_message)  # Bind to Enter key event

        # Create a ScrollView for the messages
        self.scroll_view = ScrollView(size_hint=(1, None), height=400)
        self.messages_label = Label(text='', markup=True, size_hint_y=None, valign='top', text_size=(Window.width, None), halign='left')
        self.scroll_view.add_widget(self.messages_label)

        self.layout.add_widget(self.scroll_view)
        self.layout.add_widget(self.message_input)

        # Start a Clock event to repeatedly focus the input
        self.focus_event = Clock.schedule_interval(self.set_focus, 0.1)

        server_address = ("192.168.137.109", 12345)  # Change server IP and port
        self.client_socket.connect(server_address)

        self.receive_thread = threading.Thread(target=self.receive_server_messages)
        self.receive_thread.start()

        self.client_socket.send(f"{self.nickname} entered the chat!".encode("utf-8"))

    def set_focus(self, dt):
        self.message_input.focus = True

    def on_stop(self):
        # Cancel the focus event when the app is stopped
        if self.focus_event:
            self.focus_event.cancel()
            self.focus_event = None

    def send_message(self, instance):
        message = self.message_input.text
        if message:
            self.client_socket.send(f"{self.nickname}: {message}".encode("utf-8"))
            self.messages_label.text += f'{self.nickname}: {message}\n'
            self.message_input.text = ''
            self.scroll_view.scroll_y = 0

    def receive_server_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode("utf-8")
                if message:
                    self.messages_label.text += f'{message}\n'
                    self.scroll_view.scroll_y = 0
            except:
                break

if __name__ == '__main__':
    ChatClientApp().run()
