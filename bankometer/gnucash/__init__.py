
import lxml.etree as ET
import gzip
import shutil
import datetime 


class GnuCashBook:
    def __init__(self, tree):
        """Initialize the GnuCashBook with a parsed XML tree."""
        self.tree = tree
        self.root = tree.getroot()
        self.accounts = self._parse_accounts()
        self.transactions = self._parse_transactions()
        self.prices = list(self._parse_prices())
        self.budgets = self._parse_budgets()

    @staticmethod
    def open_book(filepath):
        """Static method to open a compressed XML file and parse it."""
        temp_path = filepath + ".uncompressed"
        with gzip.open(filepath, 'rb') as f_in:
            with open(temp_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        tree = ET.parse(temp_path)
        return GnuCashBook(tree)

    def _parse_accounts(self):
        """Helper method to parse accounts from the XML tree."""
        accounts = []
        for account in self.root.findall(".//gnc:account", self.root.nsmap):
            name = account.find("act:name", self.root.nsmap).text
            account_id = account.find("act:id", self.root.nsmap).text
            parent = account.find("act:parent", self.root.nsmap)
            commodity = account.find("act:commodity", self.root.nsmap).find("cmdty:id", self.root.nsmap).text
            if parent is not None:
                parent = parent.text
            accounts.append({
                "name": name,
                "id": account_id,
                "parent": parent,
                "commodity": commodity
            })

        # Set parent as account object
        for acc in accounts:
            acc["parent"] = next((a for a in accounts if a["id"] == acc["parent"]), None)

        return [GnuCashAccount(self, acc) for acc in accounts]

    def _parse_prices(self):
        """Helper method to parse prices from the XML tree."""
        prices = []
        for price in self.root.findall(".//gnc:pricedb/price", self.root.nsmap):
            commodity_guid = price.find("price:commodity", self.root.nsmap).find("cmdty:id", self.root.nsmap).text
            currency_guid = price.find("price:currency", self.root.nsmap).find("cmdty:id", self.root.nsmap).text
            date = price.find("price:time", self.root.nsmap).find("ts:date", self.root.nsmap).text
            date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S %z")
            value = price.find("price:value", self.root.nsmap).text
            if "/" in value:
                value1, value2 = value.split("/")
                value = float(value1) / float(value2)
            else:
                value = float(value)
            prices.append({
                "commodity_guid": commodity_guid,
                "currency_guid": currency_guid,
                "date": date,
                "value": value
            })
        return reversed(sorted(prices, key=lambda p: p["date"]))
    
    def convert_commodity(self, value, from_commodity, to_currency):
        """Convert a value from one commodity to another."""
        if value == 0:
            return 0
        if from_commodity == to_currency:
            return value
        price = next(
            (p for p in self.prices if p["commodity_guid"] == from_commodity and p["currency_guid"] == to_currency),
            None
        )
        if price is None:
            # try to find reversed conversion
            price = next(
                (p for p in self.prices if p["commodity_guid"] == to_currency and p["currency_guid"] == from_commodity),
                None
            )
            if price is None:
                return None
            return value / price["value"]
        return value * price["value"]

    def get_accounts(self) -> list["GnuCashAccount"]:
        """Return all GnuCashAccount instances."""
        return self.accounts

    def get_account(self, name):
        """Return a specific account by name."""
        return next((acc for acc in self.accounts if acc.name == name), None)

    def get_account_by_id(self, account_id):
        """Return a specific account by ID."""
        return next((acc for acc in self.get_accounts() if acc.id == account_id), None)

    def _parse_transactions(self) -> list["GnuCashTransaction"]:
        """Helper method to parse transactions from the XML tree."""
        transactions = []
        for transaction in self.root.findall(".//gnc:transaction", self.root.nsmap):
            transactions.append(GnuCashTransaction(self, transaction))
        return transactions

    def _parse_budgets(self):
        """Helper method to parse budgets from the XML tree."""
        budgets = []
        for budget in self.root.findall(".//gnc:budget", self.root.nsmap):
            name = budget.find("bgt:name", self.root.nsmap).text
            budget_id = budget.find("bgt:id", self.root.nsmap).text
            slots = []
            if budget.find("bgt:slots", self.root.nsmap) is not None:
                slots = budget.find("bgt:slots", self.root.nsmap).findall("slot", self.root.nsmap)
            accounts = {}
            for slot in slots:
                account_id = slot.find("slot:key", self.root.nsmap).text
                amounts = slot.find("slot:value", self.root.nsmap).findall("slot", self.root.nsmap)
                accounts[account_id] = [
                    {
                        "amount": (amount.find("slot:value", self.root.nsmap).text),
                        "month": int(amount.find("slot:key", self.root.nsmap).text)+1,
                    } for amount in amounts
                ]
                for amount in accounts[account_id]:
                    if "/" in amount["amount"]:
                        value1, value2 = amount["amount"].split("/")
                        amount["amount"] = float(value1) / float(value2)
                    else:
                        amount["amount"] = float(amount["amount"])
            budgets.append(GnuCashBudget(self, {
                "name": name,
                "id": budget_id,
                "amount": accounts
            }))

        return budgets
    
    def get_budget_by_name(self, name):
        """Return a specific budget by name."""
        return next((budget for budget in self.budgets if budget.name == name), None)
    
    def get_budget_by_id(self, budget_id):
        """Return a specific budget by ID."""
        return next((budget for budget in self.budgets if budget.id == budget_id), None)
    
    def get_budgets(self) -> list["GnuCashBudget"]:
        """Return all budgets."""
        return self.budgets
    

                

class GnuCashBudget:
    def __init__(self, book, budget_data):
        """Initialize a GnuCashBudget."""
        self.book = book
        self.name = budget_data["name"]
        self.id = budget_data["id"]
        self.amount = budget_data["amount"]
    
    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, GnuCashBudget) and self.id == __value.id

    def get_accounts(self):
        """Return all accounts involved in the budget."""
        return [self.book.get_account_by_id(acc) for acc in self.amount.keys()]
    
    def get_budget(self, account, month):
        """Return the budget for a specific account and month."""
        return next((b["amount"] for b in self.amount[account.id] if b["month"] == month), 0)
    
    def get_total_budget(self, account):
        """Return the total budget for a specific account."""
        return sum(b["amount"] for b in self.amount[account.id])
    
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return "<GnuCashBudget(name={}, id={})>".format(self.name, self.id)

class GnuCashAccount:
    def __init__(self, book: GnuCashBook, account_data):
        """Initialize a GnuCashAccount."""
        self.book = book
        self.name = account_data["name"]
        self.id = account_data["id"]
        self.parent = account_data["parent"]
        self.commodity = account_data["commodity"]
        
    
    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, GnuCashAccount) and self.id == __value.id

    def get_parent(self):
        """Return the parent account."""
        return self.book.get_account_by_id(self.parent["id"]) if self.parent is not None else None

    def get_transactions(self) -> list["GnuCashTransaction"]:
        """Return all transactions involving this account."""
        tx =  [
            txn for txn in self.book.transactions
            if any(credit["account"].id == self.id for credit in txn.get_credits())
        ]
        tx = sorted(tx, key=lambda t: t.date_posted)
        return tx

    def get_incoming_transactions(self) -> list["GnuCashTransaction"]:
        """Return all incoming transactions to this account."""
        tx =  [
            txn for txn in self.book.transactions
            if any(debit["account"].id == self.id for debit in txn.get_debits())
        ]
        tx = sorted(tx, key=lambda t: t.date_posted)
        
        return tx
    
    def get_full_name(self):
        """Return the full account name including parent accounts."""
        parent_chain = []
        current = self
        while current is not None:
            parent_chain.append(current.name)
            current = current.get_parent()
        return ":".join(list(reversed(parent_chain))[1:])
    
    def get_level(self):
        """Return the account level in the hierarchy."""
        level = 0
        current = self
        while current is not None:
            level += 1
            current = current.get_parent()
        return level

    def get_children(self):
        """Return all child accounts."""
        return [acc for acc in self.book.accounts if acc.get_parent() == self]
    
    def get_balance(self, date=None):
        """Return the account balance at a specific date."""
        balance = 0
        if len(self.get_children()) > 0:
            for child in self.get_children():
                balance += self.book.convert_commodity(child.get_balance(date), child.commodity, self.commodity)
            return balance
        for txn in self.get_transactions():
            if date is not None and txn.date_posted > date:
                continue
            for credit in txn.get_credits():
                if credit["account"] == self:
                    balance += credit["value"]
        for txn in self.get_incoming_transactions():
            if date is not None and txn.date_posted > date:
                continue
            for debit in txn.get_debits():
                if debit["account"] == self:
                    balance += debit["value"]
        return balance

class GnuCashTransaction:
    def __init__(self, book, transaction_element):
        """Initialize a GnuCashTransaction with the transaction XML element."""
        self.book = book
        self.id = transaction_element.find("trn:id", book.root.nsmap).text
        self.date_posted = transaction_element.find("trn:date-posted", book.root.nsmap).find("ts:date", book.root.nsmap).text
        self.date_posted = datetime.datetime.strptime(self.date_posted, "%Y-%m-%d %H:%M:%S %z").date()
        self.description = transaction_element.find("trn:description", book.root.nsmap).text
        self.splits = self._parse_splits(transaction_element)

    def __str__(self):
        return self.description if self.description is not None else "No description"
    def __repr__(self):
        return "<GnuCashTransaction(id={}, date_posted={}, description={})>".format(self.id, self.date_posted, self.description)

    def _parse_splits(self, transaction_element):
        """Helper method to parse splits for the transaction."""
        splits = []
        split_elements = transaction_element.findall("trn:splits/trn:split", self.book.root.nsmap)
        for split in split_elements:
            value = split.find("split:quantity", self.book.root.nsmap).text
            if "/" in value:
                value1, value2 = value.split("/")
                value = float(value1) / float(value2)
            else:
                value = float(value)
            account_id = split.find("split:account", self.book.root.nsmap).text
            account = next(acc for acc in self.book.accounts if acc.id == account_id)
            splits.append({
                "account": account,
                "value": value
            })
        return splits

    def get_debits(self):
        """Return all debit entries (positive values)."""
        return [split for split in self.splits if split["value"] > 0]

    def get_credits(self):
        """Return all credit entries (negative values)."""
        return [split for split in self.splits if split["value"] < 0]

