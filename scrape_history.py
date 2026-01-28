import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

# --- CONFIG ---
DATA_DIR = "./data"
MAIN_URL = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
BASE_URL = "https://www.federalreserve.gov"

def download_pdf(url, filename):
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        print(f"⏩ Skipping {filename} (Already exists)")
        return
        
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"✅ Downloaded: {filename}")
        else:
            print(f"⚠️ Failed. Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error downloading {url}: {e}")

def scrape_fed_history():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    print(f"🦅 Starting Scrape of: {MAIN_URL}")
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(MAIN_URL, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all PDF links
        pdf_links = soup.find_all('a', href=True)
        print(f"🔎 Scanning {len(pdf_links)} links for Minutes...")
        
        count = 0
        for link in pdf_links:
            href = link['href']
            
            # The Magic Regex: matches "fomcminutes" followed by exactly 8 digits
            date_match = re.search(r'fomcminutes(\d{8})\.pdf', href, re.IGNORECASE)
            
            if date_match:
                date_str = date_match.group(1)  # e.g., "20250129"
                year = date_str[:4]
                month = date_str[4:6]
                day = date_str[6:8]
                
                # Only keep recent history (2020+)
                if int(year) >= 2020:
                    pdf_url = urljoin(BASE_URL, href)
                    filename = f"{year}-{month}-{day}_minutes.pdf"
                    download_pdf(pdf_url, filename)
                    count += 1
        
        print(f"\n🎉 Finished! Downloaded {count} documents.")

    except Exception as e:
        print(f"❌ Critical Error: {e}")

if __name__ == "__main__":
    scrape_fed_history()