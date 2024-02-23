import json

from anvil.tables import app_tables
from kivy.core.window import Window
from kivymd.uix.screen import MDScreen

from libs.uix.root import Root
from server import Server


class Login(MDScreen):
    def __init__(self, **kwargs):
        super(Login, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_keyboard)
        self.server = Server()

    def on_keyboard(self, instance, key, scancode, codepoint, modifier):
        if key == 27:  # Keycode for the back button on Android
            self.on_back_button()
            return True
        return False

    def on_back_button(self):
        self.manager.push_replacement("main_sc","right")

    # def google_sign_in(self):
    #     # Set up the OAuth 2.0 client ID and client secret obtained from the Google Cloud Console
    #     client_id = "749362207551-tdoq2d8787csqqnbvpdgcc3m2sdtsnd1.apps.googleusercontent.com"
    #     client_secret = "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"
    #     redirect_uri = "https://oxivive.com/oauth/callback"
    #     redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
    #
    #     # Set up the Google OAuth flow
    #     flow = InstalledAppFlow.from_client_secrets_file(
    #         "client_secret.json",
    #         scopes=["https://www.googleapis.com/auth/userinfo.email"],
    #         redirect_uri=redirect_uri
    #     )
    #
    #     # Get the authorization URL
    #     auth_url, _ = flow.authorization_url(prompt="select_account")
    #     print(f"Authorization URL: {auth_url}")
    #
    #     # Open a web browser to the authorization URL
    #     webbrowser.open(auth_url)
    #
    #     # Get the authorization code from the user
    #     authorization_code = input("Enter the authorization code: ")
    #
    #     # Exchange the authorization code for credentials
    #     credentials = flow.fetch_token(
    #         token_uri="https://oauth2.googleapis.com/token",
    #         authorization_response=authorization_code
    #     )
    #
    #     # Use the obtained credentials for further Google API requests
    #     # Example: print the user's email address
    #     user_email = credentials.id_token["email"]
    #     print(f"User email: {user_email}")
    #
    # def exchange_code_for_tokens(self, authorization_code):
    #     token_url = "https://oauth2.googleapis.com/token"
    #
    #     params = {
    #         "code": authorization_code,
    #         "client_id": "your_client_id",
    #         "client_secret": "your_client_secret",
    #         "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
    #         "grant_type": "authorization_code"
    #     }
    #
    #     response = requests.post(token_url, data=params)
    #     token_data = response.json()
    #
    #     return token_data


    def login_page(self, instance, *args):
        email = self.ids.login_email.text
        password = self.ids.login_password.text
        if len(email) == 0 and len(password) == 0:
            # Login failed
            self.ids.login_email.error = True
            self.ids.login_email.helper_text = "Invalid email or password"
            self.ids.login_password.error = True
            print("Enter Email and Password")
        elif len(email) >= 0 and len(password) >= 0:
            user_anvil = None
            user_sqlite = None
            try:
                if self.server.is_connected():
                    # Fetch user from Anvil's database
                    user_anvil = app_tables.users.get(
                        email=email,
                        password=password,
                    )
                else:
                    # Fetch user from SQLite database
                    cursor = self.server.get_database_connection().cursor()
                    cursor.execute('''
                                SELECT * FROM users
                                WHERE email = ? AND password = ?
                            ''', (email, password))
                    user_sqlite = cursor.fetchone()
            finally:
                # Close the connection
                if self.server.get_database_connection() and self.server.is_connected():
                    self.server.get_database_connection().close()

            if user_anvil or user_sqlite:
                print("Login successful.")
                self.manager.push("client_services")
                if user_anvil:
                    username = str(user_anvil["username"])
                    email = str(user_anvil["email"])
                    password = str(user_anvil["password"])
                    phone = str(user_anvil["phone"])
                    pincode = str(user_anvil["pincode"])
                if user_sqlite:
                    username = user_sqlite[1]
                    email = user_sqlite[2]
                    password = user_sqlite[3]
                    phone = user_sqlite[4]
                    pincode = user_sqlite[0]
                    print(f"hi {username}")
                logged_in = True
                self.manager.load_screen("menu_profile")
                logged_in_data = {'logged_in': logged_in}
                user_info = {'username': username, 'email': email, 'phone': phone, 'pincode': pincode,
                             'password': password}
                with open("logged_in_data.json", "w") as json_file:
                    json.dump(logged_in_data, json_file)
                with open("user_data.json", "w") as json_file:
                    json.dump(user_info, json_file)
                screen = self.manager.get_screen("client_services")
                screen.ids.username.text = user_info['username']
                screen.ids.email.text = user_info['email']

            else:
                # Login failed
                self.ids.login_email.error = True
                self.ids.login_email.helper_text = "Invalid email or password"
                self.ids.login_password.error = True