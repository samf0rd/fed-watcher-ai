import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Base URL for the Fed's meeting calendars
BASE_URL = "https://www.federalreserve.gov"
CALENDAR_URL = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
DATA_DIR = "./data"

def download_pdf(url, filename):
    response = requests.get(url) #send a GET request to the URL, download the pdf and save it in response.content
    if response.status_code == 200: #check if the request was successful
        filepath = os.path.join(DATA_DIR, filename) #creates a string path to the file, this is the destination location
        with open(filepath, 'wb') as f: #open the file in binary mode, this is the file to write the content to
            f.write(response.content) #write the content to a file
        print(f"✅ Downloaded: {filename}")
        return filepath #return the path to the file
    else:
        print(f"❌ Failed to download {url}")
        return None

def scrape_latest_minutes():
    # 1. Ensure data directory exists
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    print("🦅 Scouting the Fed website for Minutes...")
    
    # 2. Get the HTML of the calendar page
    response = requests.get(CALENDAR_URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 3. Find the links to "Minutes" (usually PDF)
    # The Fed website structure often puts minutes in links containing 'fomcminutes' and ending in .pdf
    # We look for the first one we find (which is usually the most recent meeting)
    
    pdf_link = None
    pdf_name = None

    for link in soup.find_all('a', href=True): #find all the links in the soup, this is a list of all the links in the page
        href = link['href'] #get the href attribute of the link
        if 'fomcminutes' in href and href.endswith('.pdf'): #check if the link contains 'fomcminutes' and ends with .pdf
            pdf_link = urljoin(BASE_URL, href) #join the base url with the href, this is the full url of the link
            # Extract a nice name like "20231213_minutes.pdf"
            pdf_name = href.split('/')[-1] #split the href by '/' and get the last part, this is the name of the file
            print(f"🎯 Found target: {pdf_name}") #print the name of the file
            break #break the loop if the link is found
    
    if pdf_link: #if the link is found, download the pdf
        download_pdf(pdf_link, pdf_name)
    else:
        print("⚠️ No Minutes PDF found on the main calendar page.")

if __name__ == "__main__":
    scrape_latest_minutes()