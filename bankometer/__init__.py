
import datetime
from decimal import Decimal
import pandas as pd 

import piecash

import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.orm.dynamic

from bankometer import objdiff
from bankometer.config import get_config_dict


def getattrs(obj):
    return {
        a: getattr(obj, a) for a in dir(obj) if not a.startswith("__") and not callable(getattr(obj, a))
    }
def get_account(account):
    aliases = get_config_dict("account_aliases", {}, "Aliases for accounts in gnucash file")
    if account in aliases:
        return aliases[account]
    return account
class Methods:
    
    def accounts(self, gnucash_file: str):
        """
        Returns accounts from gnucash file.
        """
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

    def transactions(self, gnucash_file: str, *, account: str = ""):
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

    def balances(self, gnucash_file: str, *, traditional: bool = False):
        """
        Returns balances of all accounts in gnucash file.
        """
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
        accounts = self.accounts(gnucash_file)
        data = [] 
        for account in accounts:
            balance = 0 
            for transaction in self.transactions(gnucash_file, account=account["name"]):
                if transaction["account_amount"] is not None:
                    balance += transaction["account_amount"]
            data.append({
                "name": account["name"],
                "balance": balance
            })
        return data

    def add_transaction(self, gnucash_file: str, source: str, target: str, 
            amount: float, description: str, *, currency: str = "RSD"):
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
