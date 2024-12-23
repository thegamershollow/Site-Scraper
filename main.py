import requests
from bs4 import BeautifulSoup
import time
import urllib.parse

# Function to scrape a single page
def scrape_page(url, visited, all_urls):
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
                    all_urls.add(full_url)
    except requests.RequestException as e:
        # Suppress minor exceptions and log only the critical ones
        print(f"Error scraping {url}: {e}", file=open("scraper_errors.txt", "a"))

# Main function to start scraping
def scrape_website(start_url):
    visited = set()  # Set to track visited URLs
    all_urls = set()  # To store all discovered URLs

    # Scrape only the starting page's links (no recursion into subpages)
    scrape_page(start_url, visited, all_urls)

    return all_urls

# Save scraped URLs to a file with the format: scraped_pages_<start_url>.txt
def save_results(urls, start_url):
    filename = f"scraped_pages_{start_url.replace('https://', '').replace('http://', '').replace('/', '_')}.txt"
    with open(filename, 'w', encoding='utf-8') as file:
        for url in urls:
            file.write(url + "\n")

if __name__ == "__main__":
    start_url = input("Enter the starting URL: ")
    start_time = time.time()  # Start measuring time
    urls = scrape_website(start_url)  # Start scraping
    save_results(urls, start_url)  # Save results to a file
    end_time = time.time()  # End measuring time

    elapsed_time = end_time - start_time  # Calculate elapsed time
    print(f"Scraping completed in {elapsed_time:.2f} seconds.")
