import time
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


class GenericWebScraper:
    def __init__(self):
        self.visited_urls = set()
        self.scraped_data = []

        # Requests session with retry mechanism
        self.session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=2,
            status_forcelist=[500, 502, 503, 504]
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

        # Set up Selenium WebDriver
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run without UI
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920x1080")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def scrape_website(self, url):
        """Main function to scrape a website and its internal links."""
        print(f"Scraping: {url}")
        if url in self.visited_urls:
            return  # Prevent duplicate scraping

        self.visited_urls.add(url)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        try:
            response = self.session.get(url, headers=headers, timeout=20)
            if response.status_code in [406, 403]:  # Some websites block scrapers
                print(f"Skipping {url}: HTTP {response.status_code} (Blocked)")
                return

            if response.status_code != 200:
                print(f"Skipping {url}: HTTP {response.status_code}")
                return

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract all text content
            self.extract_text_content(soup, url)

            # Find and scrape internal links
            self.scrape_internal_links(soup, url)
            time.sleep(2)

        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            self.scrape_with_selenium(url)

    def scrape_with_selenium(self, url):
        """Handles JavaScript-rendered pages using Selenium."""
        print(f"Trying Selenium for {url}...")
        try:
            self.driver.get(url)


            
            time.sleep(5)  # Allow time for JavaScript to load

            # Scroll to bottom to load dynamic content
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            self.extract_text_content(soup, url)
        except Exception as e:
            print(f"Selenium scraping failed for {url}: {e}")

    def extract_text_content(self, soup, url):
        """Extracts all text-based content from the webpage, including prices and discounts."""
        content = []

        for element in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "td", "th", "small", "strike", "a"]):
            text = element.get_text(strip=True)
            if text:
                # Tagging prices or discounts for better clarity
                if element.name == "small" and any(char.isdigit() for char in text):
                    content.append(f"💸 Price: {text}")
                elif element.name == "strike" and any(char.isdigit() for char in text):
                    content.append(f"❌ Original Fee: {text}")
                else:
                    content.append(text)

        if content:
            self.scraped_data.append({"url": url, "content": content})

    def scrape_internal_links(self, soup, base_url):
        """Finds and scrapes internal links for better coverage."""
        for link in soup.find_all("a", href=True):
            href = link["href"]
            full_url = urljoin(base_url, href)

            if urlparse(full_url).netloc == urlparse(base_url).netloc and full_url not in self.visited_urls:
                self.scrape_website(full_url)

    def save_data(self, filename="webscrapingTS.json"):
        """Saves the scraped data in JSON format."""
        with open(filename, "w", encoding="utf-8") as json_file:
            json.dump(self.scraped_data, json_file, indent=4, ensure_ascii=False)
        print(f"Data saved to {filename}")

    def close(self):
        self.driver.quit()


if __name__ == "__main__":
    url = "https://talentspiral.com"  # Change this to the target website
    scraper = GenericWebScraper()
    scraper.scrape_website(url)
    scraper.save_data()
    scraper.close()
