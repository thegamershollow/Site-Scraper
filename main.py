import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import urllib.parse

# Function to scrape a single page
def scrape_page(url, visited, urls_to_scrape, all_urls):
    if url in visited:
        return
    visited.add(url)

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Add the URL to the list of all URLs
            all_urls.add(url)

            # Find all links on the page
            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href']
                # Resolve relative URLs
                full_url = urllib.parse.urljoin(url, href)
                # Only add valid HTTP URLs to scrape list
                if full_url.startswith('http') and full_url not in visited:
                    urls_to_scrape.add(full_url)
    except requests.RequestException as e:
        print(f"Error scraping {url}: {e}")

# Main function to start scraping
def scrape_website(start_url):
    visited = set()  # Set to track visited URLs
    urls_to_scrape = {start_url}  # Set to keep track of URLs to scrape
    all_urls = set()  # To store all discovered URLs

    # Use a ThreadPoolExecutor to scrape multiple pages concurrently
    with ThreadPoolExecutor(max_workers=10) as executor:
        while urls_to_scrape:
            futures = []
            # Submit tasks for all URLs currently in the scraping list
            while urls_to_scrape:
                url = urls_to_scrape.pop()
                futures.append(executor.submit(scrape_page, url, visited, urls_to_scrape, all_urls))
            
            # Wait for all the futures to complete
            for future in as_completed(futures):
                future.result()  # If any exception was raised during scraping, it will be raised here.

    return all_urls

# Save scraped URLs to a file
def save_results(urls, filename='scraped_urls.txt'):
    with open(filename, 'w', encoding='utf-8') as file:
        for url in urls:
            file.write(url + "\n")

if __name__ == "__main__":
    start_url = input("Enter the starting URL: ")
    start_time = time.time()
    urls = scrape_website(start_url)
    save_results(urls)
    print(f"Scraping completed in {time.time() - start_time:.2f} seconds.")
