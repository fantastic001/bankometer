
from bankometer import BankInterface

class Yettel(BankInterface):
    def get_balance(self):
        raise NotImplementedError()
    def get_transactions(self):
        raise NotImplementedError()
    def login(self):
        print("Logging in to Yettel")