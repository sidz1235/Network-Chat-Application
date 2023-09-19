from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
import json
import os
import socket
import threading


class LoginSignupApp(App):
    def build(self):
        self.title = "Login / Signup"
        self.layout = BoxLayout(orientation="vertical", spacing=10)
        
        self.username_input = TextInput(hint_text="Username", multiline=False)
        self.password_input = TextInput(hint_text="Password", password=True, multiline=False)
        
        self.login_button = Button(text="Login")
        self.signup_button = Button(text="Signup")
        
        self.login_button.bind(on_press=self.login)
        self.signup_button.bind(on_press=self.signup)
        
        self.layout.add_widget(Label(text="Welcome! Choose an option:"))
        self.layout.add_widget(self.login_button)
        self.layout.add_widget(self.signup_button)
        
        return self.layout
    
    def login(self, instance):
        self.layout.clear_widgets()
        
        self.layout.add_widget(Label(text="Login"))
        self.layout.add_widget(self.username_input)
        self.layout.add_widget(self.password_input)
        
        login_button = Button(text="Login")
        login_button.bind(on_press=self.perform_login)
        self.layout.add_widget(login_button)
        
    def signup(self, instance):
        self.layout.clear_widgets()
        
        self.layout.add_widget(Label(text="Signup"))
        self.layout.add_widget(self.username_input)
        self.layout.add_widget(self.password_input)
        
        signup_button = Button(text="Signup")
        signup_button.bind(on_press=self.perform_signup)
        self.layout.add_widget(signup_button)
        
    def perform_login(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        
        # Load user data from JSON file
        user_data = self.load_user_data()
        
        if username in user_data and user_data[username] == password:
            self.show_popup("Login Successful", "Welcome, " + username)
            self.show_user_details_input(username)
        else:
            self.show_popup("Login Failed", "Invalid username or password")
    
    def perform_signup(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        
        # Load existing user data
        user_data = self.load_user_data()
        
        if username in user_data:
            self.show_popup("Signup Failed", "Username already exists")
        else:
            user_data[username] = password
            self.save_user_data(user_data)
            self.show_popup("Signup Successful", "Account created for " + username)
            self.show_user_details_input(username)
    
    def load_user_data(self):
        try:
            with open("users.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
    
    def save_user_data(self, user_data):
        with open("users.json", "w") as file:
            json.dump(user_data, file)
    
    def show_popup(self, title, message):
        popup_layout = BoxLayout(orientation="vertical", spacing=10)
        popup_layout.add_widget(Label(text=message))
        close_button = Button(text="Close")
        popup_layout.add_widget(close_button)
        popup = Popup(title=title, content=popup_layout, size_hint=(None, None), size=(400, 200))
        close_button.bind(on_press=popup.dismiss)
        popup.open()

    def show_user_details_input(self, username):
        self.layout.clear_widgets()

        bio_input = TextInput(hint_text="Bio", multiline=True)
        place_input = TextInput(hint_text="Place", multiline=False)
        budget_input = TextInput(hint_text="Budget", multiline=False)

        submit_button = Button(text="Submit")
        submit_button.bind(on_press=lambda instance: self.save_user_details(username, bio_input.text, place_input.text, budget_input.text))

        self.layout.add_widget(Label(text=f"Welcome, {username}! Please provide your details:"))
        self.layout.add_widget(bio_input)
        self.layout.add_widget(place_input)
        self.layout.add_widget(budget_input)
        self.layout.add_widget(submit_button)
    
    def save_user_details(self, username, bio, place, budget):
        user_details = {
            'bio': bio,
            'place': place,
            'budget': budget
        }

        with open(f"{username}_details.json", "w") as file:
            json.dump(user_details, file)
        
        self.show_popup("Details Saved", "User details saved!")
        lets_chat_button = Button(text="Let's get Chatting")
        lets_chat_button.bind(on_press=lambda instance: self.launch_chat_client())
        self.layout.add_widget(lets_chat_button)

    def launch_chat_client(self):
        # Check if the server is active
        server_status = self.check_server_status()

        if server_status:
            self.stop()  # Close the current app
            os.system("python client.py")
        else:
            self.start_server()
            self.show_popup("Server Started", "The chat server is now active. You can launch the chat client.")

    def check_server_status(self):
        try:
            # Try to connect to the server
            server_address = ("192.168.137.109", 12345)  # Change server IP and port
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(server_address)
            client_socket.close()
            return True
        except:
            return False
    
    def start_server(self):
        server_thread = threading.Thread(target=self.run_server)
        server_thread.start()

    def run_server(self):
        os.system("python server.py") 

if __name__ == '__main__':
    LoginSignupApp().run()