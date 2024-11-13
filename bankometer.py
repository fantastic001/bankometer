import matplotlib.pyplot as plt
import numpy as np 
import sys
from ArgumentStack import * 
calculate_monthly_by_year_rate = lambda P, r, T: P*r*(r+1)**T / ((1+r)**T - 1)
calculate_coupon = lambda P, r, T: calculate_monthly_by_year_rate(P, r/12, T)
calculate_diff = lambda P, r, T: T*calculate_coupon(P,r,T) - P

calculate_time = lambda P, r, C: - np.log(1 - P*r/12/C ) / np.log(1+r/12)

stack = ArgumentStack("Wrong command")
stack.pushCommand("diff")
stack.pushVariable("price")
stack.pushVariable("coupon")
def analyze_diff(price, coupon, **kw):
    price = float(price)
    coupon = float(coupon)
    print("Price: %f" % price)
    print("Coupon: %f" % coupon)
    x = [] 
    y = [] 
    for r in np.linspace(0.01, 0.04, 300):
        x.append(r)
        T = calculate_time(price, r, coupon)
        y.append(calculate_diff(price, r, T))
    plt.grid()
    plt.plot(x,y)
    plt.title("Difference depending on interest rate for P=%f and T=%d" % (price, T))
    plt.show()

stack.assignAction(analyze_diff, "Analyze how much do you pay to bank additionally based on interest rate")

stack.pop()
stack.pop()
stack.pop()

stack.pushCommand("calculate")
stack.pushVariable("price")
stack.pushVariable("rate")
stack.pushVariable("coupon")
def analyze(price, rate, coupon, **kw):
    price = float(price)
    coupon = float(coupon)
    rate = float(rate)
    print("Giving to bank total: %f" % calculate_diff(price, rate, calculate_time(price, rate, coupon)))
    print("Time in moths: %f" % calculate_time(price, rate, coupon))
stack.assignAction(analyze, "Show number of months for given rate, price and coupon")

stack.popAll()

stack.pushCommand("transactions")
stack.pushVariable("gnucash_file")
def analyze_gnucash(gnucash_file, **kw):
    import piecash
    book = piecash.open_book(gnucash_file)
    transactions = book.transactions
    for transaction in transactions:
        print(transaction.description)
        print(transaction.splits)
        print(transaction.post_date)
        print("")
stack.assignAction(analyze_gnucash, "Show transactions from gnucash file")

stack.popAll()

stack.pushCommand("new")
stack.pushVariable("gnucash_file")
stack.pushVariable("source")
stack.pushVariable("destination")
stack.pushVariable("amount")
stack.pushVariable("description")
def add_transaction(gnucash_file, source, destination, amount, description, **kw):
    import piecash
    import datetime 

    my_currency = "RSD"
    amount = int(amount)
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
stack.assignAction(add_transaction, "Add transaction to gnucash file")


stack.popAll()

stack.pushCommand("help")
stack.assignAction(lambda **kw: print(stack.getHelp()), "Get help")

stack.popAll()
stack.execute(sys.argv)