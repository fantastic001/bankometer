
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

def main():
    driver = start_browser()
    account_id = None 
    try:
        # Navigate to login page
        login_url = "https://online.mobibanka.rs/Identity"
        driver.get(login_url)
        
        print("Waiting for user to log in...")
        # wait for element //*[@id="main"]/div[2]/div/div[1]/section/div/div[1]/div/div/div/div[1]/div[1]/p
        while True:
            try:
                # try to find element with attribute data-accountid 
                root = driver.find_element(By.XPATH, '//*[@data-accountid]')
                account_id = root.get_attribute('data-accountid')
                print("Account ID: ", account_id)
                break
            except:
                time.sleep(1)
                continue
        

        # Sniff network requests (if needed)
        sniff_requests(driver)

        # Capture cookies after login
        cookies = capture_cookies(driver)
        for cookie in cookies:
            print(cookie["name"], cookie["value"])
        
        session = requests.Session()
        for cookie in cookies:
            session.cookies.set(cookie["name"], cookie["value"])
        
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
            'DateFrom': '22/10/2024',
            'DateTo': '21/11/2025',
            'CurrencyList_input': 'Sve valute',
            'CurrencyList': '',
            'AmountFrom': '',
            'AmountTo': '',
            'Direction': '',
            'TransactionType': '-1',
            'AccountPicker': account_id,
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
        response = session.post(url, headers=headers, data=data)
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
            response = session.get(csv_url)
            print("CSV: ", response.text)
        else:
            print("CSV not found")

    except Exception as e:
        raise 
        

    finally:
        # Close the browser
        print("Closing browser...")
        driver.quit()


class Yettel(BankInterface):
    def get_balance(self):
        raise NotImplementedError()
    def get_transactions(self):
        raise NotImplementedError()
    def login(self):
        print("Logging in to Yettel")


if __name__ == "__main__":
    main()