import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import urllib.parse

# Function to scrape a single page
def scrape_page(url, visited, results, urls_to_scrape):
    if url in visited:
        return
    visited.add(url)
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Collect the page content (can be changed to store specific content)
            results[url] = response.text

            # Find all links on the page
            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href']
                # Resolve relative URLs
                full_url = urllib.parse.urljoin(url, href)
                if full_url.startswith('http'):
                    urls_to_scrape.add(full_url)
    except requests.RequestException as e:
        print(f"Error scraping {url}: {e}")

# Main function to start scraping
def scrape_website(start_url):
    visited = set()  # Set to track visited URLs
    results = {}     # Dictionary to store URLs and their content
    urls_to_scrape = {start_url}  # Set to keep track of URLs to scrape

    # Use a ThreadPoolExecutor to scrape multiple pages concurrently
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(scrape_page, url, visited, results, urls_to_scrape): url for url in urls_to_scrape}
        
        # Process completed futures
        for future in as_completed(futures):
            url = futures[future]
            try:
                future.result()  # Raise any exception caught during scraping
            except Exception as e:
                print(f"Error processing {url}: {e}")
            
    return results

# Save scraped content to a file
def save_results(results, filename='scraped_pages.txt'):
    with open(filename, 'w', encoding='utf-8') as file:
        for url, content in results.items():
            file.write(f"URL: {url}\n")
            file.write(content)
            file.write("\n" + "="*80 + "\n")

if __name__ == "__main__":
    start_url = input("Enter the starting URL: ")
    start_time = time.time()
    results = scrape_website(start_url)
    save_results(results)
    print(f"Scraping completed in {time.time() - start_time:.2f} seconds.")
