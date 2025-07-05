
import datetime
from decimal import Decimal
import pandas as pd 

import piecash

import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.orm.dynamic

from bankometer import objdiff
from bankometer.config import get_config_dict, get_config_str
from orgasm.http_rest import http_get, http_post


DEFAULT_GNUCASH_FILE = get_config_str(
    "gnucash_file", 
    "bankometer.gnucash",
    "Path to gnucash file, used for storing transactions and accounts"
)

def getattrs(obj):
    return {
        a: getattr(obj, a) for a in dir(obj) if not a.startswith("__") and not callable(getattr(obj, a))
    }

def get_aliases():
    return get_config_dict("account_aliases", {}, "Aliases for accounts in gnucash file")

def get_account(account):
    aliases = get_aliases()
    if account in aliases:
        return aliases[account]
    return account

def is_child(parent, child):
    """
    Check if parent is a parent of child in gnucash account hierarchy.

    Example:
        is_child("Assets:Bank:MyBank", "Assets:Bank:MyBank:Checking")


    Args:
        parent (str): Full name of the parent account.
        child (str): Full name of the child account.
    Returns:
        bool: True if parent is a parent of child, False otherwise.
    """
    if not parent or not child:
        return False
    if parent == child:
        return True
    p = parent.split(":")
    c = child.split(":")
    if len(p) >= len(c):
        return False
    for i in range(len(p)):
        if p[i] != c[i]:
            return False
    return True


class Methods:
    
    def aliases(self):
        """
        Returns aliases for accounts in gnucash file.
        """
        aliases = get_aliases()
        data = []
        for alias, account in aliases.items():
            data.append({
                "alias": alias,
                "account": account
            })
        return data

    def accounts(self):
        """
        Returns accounts from gnucash file.
        """
        gnucash_file = DEFAULT_GNUCASH_FILE
        book = piecash.open_book(gnucash_file)
        data = [] 
        for account in book.accounts:
            prices: sqlalchemy.orm.dynamic.AppenderQuery = account.commodity.prices if account.commodity else None # type: ignore
            
            default_currency =  not prices or not prices.first()
            data.append({
                "name": account.fullname,
                "currency": account.commodity.fullname, 
                # "account": getattrs(account), 
                "currency_price": 1 if default_currency else prices.first().value,
                "price_in": prices.first().currency.fullname if not default_currency else account.commodity.fullname
                # "currency": account.currency.mnemonic if account.currency else None
            })
        return data 

    @http_get
    def transactions(self, *, account: str = ""):
        gnucash_file = DEFAULT_GNUCASH_FILE
        account = get_account(account)
        book = piecash.open_book(gnucash_file)
        transactions = book.transactions
        data = [] 
        for transaction in transactions:
            if account and not any(split.account.fullname == account for split in transaction.splits):
                continue
            if not transaction.splits:
                continue
            if not transaction.post_date:
                continue

            data.append({
                "description": transaction.description,
                "post_date": transaction.post_date,
                "amount": sum(split.quantity for split in transaction.splits if split.value > 0),
                "account_amount": sum(split.quantity for split in transaction.splits if split.account.fullname == account) if account else None
            })
        return sorted(data, key=lambda x: x["post_date"], reverse=False)

    @http_get
    def balances(self, *, traditional: bool = False):
        """
        Returns balances of all accounts in gnucash file.
        """
        gnucash_file = DEFAULT_GNUCASH_FILE
        if traditional:
            from bankometer.gnucash import GnuCashBook
            book = GnuCashBook.open_book(gnucash_file)
            accounts = book.get_accounts()
            data = []
            for account in accounts:
                data.append({
                    "name": account.get_full_name(),
                    "balance": account.get_balance()
                })
            return data
        accounts = self.accounts()
        data = [] 
        for account in accounts:
            balance = 0 
            for transaction in self.transactions(account=account["name"]):
                if transaction["account_amount"] is not None:
                    balance += transaction["account_amount"]
            data.append({
                "name": account["name"],
                "balance": balance
            })
        return data

    def add_transaction(self, source: str, target: str,
            amount: float, description: str, *, currency: str = "RSD"):
        gnucash_file = DEFAULT_GNUCASH_FILE
        destination = target
        old_balance = self.balances(gnucash_file)
        amount: Decimal = Decimal("%f" % amount)
        source = get_account(source)
        destination = get_account(destination)
        book = piecash.open_book(gnucash_file, readonly=False)
        my_currency = currency
        currency = None 
        for c in book.currencies:
            if my_currency in c.mnemonic:
                currency = c
                break
        if currency is None:
            print("Currency not found")
            return
        source_account = next(filter(lambda x: source in x.fullname, book.accounts))
        destination_account = next(filter(lambda x: destination in x.fullname, book.accounts))
        book.transactions.append(piecash.Transaction(
            currency=currency,
            post_date=datetime.datetime.now().date(),
            description=description,
            splits=[
                piecash.Split(account=source_account, value=-amount),
                piecash.Split(account=destination_account, value=amount)
            ]
        ))
        book.save()
        new_balance = self.balances(gnucash_file)
        balance_diff = objdiff.diff(old_balance, new_balance)
        return balance_diff

    