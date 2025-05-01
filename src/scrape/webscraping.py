import time
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


## <---------- Initialization Section ---------->
class GenericWebScraper:
    def __init__(self):
        """Initializes the scraper, setting up session and WebDriver."""
        self.visited_urls = set()  # Track visited URLs to avoid re-scraping
        self.scraped_data = []  # Store the scraped content

        ## <---------- Set up Requests session with retry mechanism ---------->        
        self.session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=2,
            status_forcelist=[500, 502, 503, 504]
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

        ## <---------- Set up Selenium WebDriver for JavaScript rendering ---------->        
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run without UI (headless mode)
        chrome_options.add_argument("--disable-gpu")  # Disable GPU for better performance in headless mode
        chrome_options.add_argument("--no-sandbox")  # Avoid sandbox issues
        chrome_options.add_argument("--window-size=1920x1080")  # Set window size for web scraping
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


## <---------- Scraping Logic Section ---------->

    def scrape_website(self, url):
        """Main function to scrape a website and its internal links."""
        print(f"Scraping: {url}")
        if url in self.visited_urls:  # Prevent scraping of already visited URLs
            return

        self.visited_urls.add(url)  # Mark the URL as visited
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        try:
            ## <---------- Request the page using requests ---------->        
            response = self.session.get(url, headers=headers, timeout=20)
            
            ## <---------- Handle blocked requests (e.g., HTTP 403 or 406) ---------->            
            if response.status_code in [406, 403]:  # Some websites block scrapers
                print(f"Skipping {url}: HTTP {response.status_code} (Blocked)")
                return

            if response.status_code != 200:  # If status is not 200, skip the URL
                print(f"Skipping {url}: HTTP {response.status_code}")
                return

            ## <---------- Parse page content with BeautifulSoup ---------->            
            soup = BeautifulSoup(response.text, "html.parser")

            ## <---------- Extract text content from the webpage ---------->            
            self.extract_text_content(soup, url)

            ## <---------- Find and scrape internal links for better coverage ---------->            
            self.scrape_internal_links(soup, url)
            time.sleep(2)  # Delay to avoid hitting the server too frequently

        except requests.RequestException as e:  # Handle request exceptions
            print(f"Error fetching {url}: {e}")
            ## <---------- Fallback to Selenium for JavaScript-heavy pages ---------->            
            self.scrape_with_selenium(url)

    def scrape_with_selenium(self, url):
        """Handles JavaScript-rendered pages using Selenium."""
        print(f"Trying Selenium for {url}...")
        try:
            ## <---------- Load the page using Selenium ---------->            
            self.driver.get(url)  
            
            time.sleep(5)  # Allow time for JavaScript to load

            ## <---------- Scroll to the bottom of the page to load dynamic content ---------->            
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

            ## <---------- Parse the page source using BeautifulSoup after JavaScript has loaded ---------->            
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            self.extract_text_content(soup, url)  # Extract content from the page
        except Exception as e:
            print(f"Selenium scraping failed for {url}: {e}")


## <---------- Content Extraction Section ---------->

    def extract_text_content(self, soup, url):
        """Extracts all text-based content from the webpage, including prices and discounts."""
        content = []  # List to store the extracted content

        ## <---------- Extract text from various HTML tags ---------->        
        for element in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "td", "th", "small", "strike", "a"]):
            text = element.get_text(strip=True)  # Extract text and remove leading/trailing spaces
            if text:
                # ## <---------- Tag prices or discounts for better clarity ---------->                
                # if element.name == "small" and any(char.isdigit() for char in text):
                #     content.append(f"💸 Price: {text}")
                # elif element.name == "strike" and any(char.isdigit() for char in text):
                #     content.append(f"❌ Original Fee: {text}")
                # else:
                    content.append(text)

        ## <---------- Store the extracted content if any ---------->        
        if content:
            self.scraped_data.append({"url": url, "content": content})


## <---------- Internal Link Scraping Section ---------->

    def scrape_internal_links(self, soup, base_url):
        """Finds and scrapes internal links for better coverage."""
        ## <---------- Find all internal links and scrape them recursively ---------->        
        for link in soup.find_all("a", href=True):
            href = link["href"]
            full_url = urljoin(base_url, href)  # Ensure the URL is absolute

            ## <---------- Check if the link is internal and hasn't been visited yet ---------->            
            if urlparse(full_url).netloc == urlparse(base_url).netloc and full_url not in self.visited_urls:
                self.scrape_website(full_url)  # Recursively scrape internal links


## <---------- Data Saving Section ---------->

    def save_data(self, filename="webscraping.json"):
        """Saves the scraped data in JSON format."""
        with open(filename, "w", encoding="utf-8") as json_file:
            json.dump(self.scraped_data, json_file, indent=4, ensure_ascii=False)  # Save data as JSON
        print(f"Data saved to {filename}")


## <---------- Cleanup Section ---------->

    def close(self):
        """Closes the Selenium WebDriver when scraping is done."""
        self.driver.quit()


## <---------- Main Execution Section ---------->
if __name__ == "__main__":
    url = "https://snehagupta.render.com"  # Change this to the target website
    scraper = GenericWebScraper()  # Create an instance of the scraper
    scraper.scrape_website(url)  # Start scraping the website
    scraper.save_data()  # Save the scraped data
    scraper.close()  # Close the WebDriver

