
from io import StringIO
from bankometer import BankInterface
import requests 

from seleniumwire import webdriver  # Import selenium-wire for request/response interception
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
import pandas as pd 
import datetime 

class YettelException(Exception):
    pass

def start_browser(chromedriver_path = None):
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")  # Open browser in maximized mode
    chrome_options.add_argument("--disable-infobars")  # Disable info bars
    chrome_options.add_argument("--disable-extensions")  # Disable extensions
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    return driver

def sniff_requests(driver, filter = None):
    # Intercept network requests and responses
    for request in driver.requests:
        if request.response:
            pass 
def capture_cookies(driver):
    # Extract cookies from the browser session
    cookies = driver.get_cookies()
    print("Captured Cookies:", cookies)
    return cookies

class Yettel(BankInterface):
    def get_balance(self):
        raise NotImplementedError()
    def get_transactions(self, start_date: datetime.date, end_date: datetime.date):
        url = 'https://online.mobibanka.rs/CustomerAccount/Accounts/PrintList'
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://online.mobibanka.rs'
        }
        data = {
            'PageNumber': '',
            'PageSize': '',
            'Report': 'csv',
            'PaymentDescription': '',
            'DateFrom': start_date.strftime("%d/%m/%Y"),
            'DateTo': end_date.strftime("%d/%m/%Y"),
            'CurrencyList_input': 'Sve valute',
            'CurrencyList': '',
            'AmountFrom': '',
            'AmountTo': '',
            'Direction': '',
            'TransactionType': '-1',
            'AccountPicker': self.account_id,
            'RelatedCardPicker': '-1',
            'CounterParty': '',
            'StandingOrderId': '',
            'SortBy': 'ValueDate',
            'SortAsc': 'Desc',
            'GeoLatitude': '',
            'GeoLongitude': '',
            'Radius': '2',
            'StatusPicker': 'Executed',
            'ViewPicker': 'List'
        }
        response = self.session.post(url, headers=headers, data=data)
        print("Response: ", response.text)
        print("Status code: ", response.status_code)
        # parse response hml and find div containing /CustomerAccount/Accounts/RenderDocument as text 
        csv_url = None 
        soup = BeautifulSoup(response.text, 'html.parser')
        all_divs = soup.find_all('div')
        for div in all_divs:
            children = list(div.children)
            filter_text =  "/CustomerAccount/Accounts/RenderDocument"
            if  div.attrs.get('id') == "mainContent":
                print("Found div: ", div)
                for child in children:
                    if filter_text in str(child):
                        print("Found child: ", child)
                        csv_url = "https://online.mobibanka.rs" + child.strip().replace("\n", "").replace(" ", "").replace("\t", "")
                break
        if csv_url is not None:
            print("CSV URL: ", csv_url)
            response = self.session.get(csv_url)
            df = pd.read_csv(StringIO(response.text))
            return df 
        else:
            raise YettelException("Could not find CSV URL in response")



    def login(self):
        max_wait_time = self.get_config("max_wait_time", 300)
        driver = start_browser()
        account_id = None 
        try:
            # Navigate to login page
            login_url = "https://online.mobibanka.rs/Identity"
            driver.get(login_url)
            
            print("Waiting for user to log in...")

            for i in range(max_wait_time):
                try:
                    # try to find element with attribute data-accountid 
                    root = driver.find_element(By.XPATH, '//*[@data-accountid]')
                    account_id = root.get_attribute('data-accountid')
                    print("Account ID: ", account_id)
                    break
                except:
                    time.sleep(1)
                    continue
            if account_id is None:
                raise YettelException("Could not find account ID in response")

            # Sniff network requests (if needed)
            sniff_requests(driver)

            # Capture cookies after login
            cookies = capture_cookies(driver)
            session = requests.Session()
            for cookie in cookies:
                session.cookies.set(cookie["name"], cookie["value"])
        finally:
            driver.quit()
            self.session = session
            self.account_id = account_id


if __name__ == "__main__":
    interface = Yettel({})
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=1)
    interface.login()
    data = interface.get_transactions(start_date, today)
    print(data)