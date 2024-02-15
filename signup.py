import re
from anvil.tables import app_tables
from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screen import MDScreen

from server import Server

class Signup(MDScreen):
    def __init__(self, **kwargs):
        super(Signup, self).__init__(**kwargs)
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

    def show_validation_dialog(self, message):
        # Create the dialog asynchronously
        Clock.schedule_once(lambda dt: self._create_dialog(message), 0)

    def _create_dialog(self, message):
        dialog = MDDialog(
            text=f"{message}",
            elevation=0,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())],
        )
        dialog.open()

    def users(self, instance, *args):

        username = self.ids.signup_username.text
        email = self.ids.signup_email.text
        password = self.ids.signup_password.text
        phone = self.ids.signup_phone.text
        pincode = self.ids.signup_pincode.text

        # Validation logic
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        # Enhanced password validation
        is_valid_password, password_error_message = self.validate_password(password)
        # Clear existing helper texts
        self.ids.signup_username.helper_text = ""
        self.ids.signup_email.helper_text = ""
        self.ids.signup_password.helper_text = ""
        self.ids.signup_phone.helper_text = ""
        self.ids.signup_pincode.helper_text = ""
        if not username:
            self.ids.signup_username.error = True
            self.ids.signup_username.helper_text = "Enter Name"
        elif not email or not re.match(email_regex, email):
            self.ids.signup_email.error = True
            self.ids.signup_email.helper_text = "Invalid Email"
        elif not is_valid_password:
            self.ids.signup_password.error = True
            self.ids.signup_password.helper_text = password_error_message
        elif not phone or len(phone) != 10:
            self.ids.signup_phone.error = True
            self.ids.signup_phone.helper_text = "Invalid Phone number (10 digits required)"
        elif not pincode or len(pincode) != 6:
            self.ids.signup_pincode.error = True
            self.ids.signup_pincode.helper_text = "Invalid Pincode (6 digits required)"

        else:
            # Clear any existing errors and helper texts
            self.ids.signup_username.error = False
            self.ids.signup_username.helper_text = ""
            self.ids.signup_email.error = False
            self.ids.signup_email.helper_text = ""
            self.ids.signup_password.error = False
            self.ids.signup_password.helper_text = ""
            self.ids.signup_phone.error = False
            self.ids.signup_phone.helper_text = ""
            self.ids.signup_pincode.error = False
            self.ids.signup_pincode.helper_text = ""

            # clear input texts
            self.ids.signup_username.text = ""
            self.ids.signup_email.text = ""
            self.ids.signup_password.text = ""
            self.ids.signup_phone.text = ""
            self.ids.signup_pincode.text = ""

            try:
                if self.server.is_connected():
                    # Check if email and phone already exist in the database
                    existing_email = app_tables.users.get(email=email)
                    existing_phone = app_tables.users.get(phone=float(phone))

                    if existing_email:
                        self.ids.signup_email.helper_text = "Email already registered"
                    elif existing_phone:
                        self.ids.signup_phone.helper_text = "Phone number already registered"
                    else:
                        # If not present, proceed to insert the new user
                        rows = app_tables.users.search()
                        # Get the number of rows
                        id = len(rows) + 1
                        app_tables.users.add_row(
                            id=id,
                            username=username,
                            email=email,
                            password=password,
                            phone=float(phone),
                            pincode=int(pincode))

                        # Additional SQLite insert (if needed)
                        with self.server.sqlite3_users_db() as connection:
                            cursor = connection.cursor()
                            cursor.execute('''
                                            INSERT INTO users (username, email, password, phone, pincode)
                                            VALUES (?, ?, ?, ?, ?)
                                        ''', (username, email, password, phone, pincode))
                            connection.commit()
                        # Navigate to the success screen
                        self.manager.push("login")
                else:
                    self.show_validation_dialog("No internet connection")

            except Exception as e:
                print(e)
                self.show_validation_dialog("Error processing user data")



    # password validation
    def validate_password(self, password):
        # Check if the password is not empty
        if not password:
            return False, "Password cannot be empty"
        # Check if the password has at least 8 characters
        if len(password) < 6:
            return False, "Password must have at least 6 characters"
        # Check if the password contains both uppercase and lowercase letters
        if not any(c.isupper() for c in password) or not any(c.islower() for c in password):
            return False, "Password must contain uppercase, lowercase"
        # Check if the password contains at least one digit
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        # Check if the password contains at least one special character
        special_characters = r"[!@#$%^&*(),.?\":{}|<>]"
        if not re.search(special_characters, password):
            return False, "Password must contain a special character"
        # All checks passed; the password is valid
        return True, "Password is valid"
