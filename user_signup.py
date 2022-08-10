from user import User
from data_manager import DataManager

class UserSignup:
    def __init__(self):
        self.dm = DataManager()

    def signup(self):
        first_name = input('First Name: ')
        last_name = input('Last Name: ')
        email = input('Email: ')
        confirm_email = input('Confirm Email: ')
        if email == confirm_email:
            new_user = User(first_name, last_name, email)
            self.dm.add_user(new_user)
