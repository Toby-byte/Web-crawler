import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

def is_valid_url(base, url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and parsed.netloc != base

def get_links_from_page(base_url, url):
    page_links = set()
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            for a_tag in soup.find_all('a', href=True):
                href = a_tag.attrs['href']
                joined_url = urljoin(base_url, href)
                if not is_valid_url(urlparse(base_url).netloc, joined_url):
                    page_links.add(joined_url)
    except Exception as e:
        print(f"An error occurred: {e}")
    return page_links

def generate_sitemap(start_url, max_workers=10):
    sitemap = set()
    to_crawl = {start_url}
    base_url = start_url

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        while to_crawl:
            batch_to_crawl = set(list(to_crawl)[:max_workers])
            to_crawl -= batch_to_crawl

            future_to_url = {executor.submit(get_links_from_page, base_url, url): url for url in batch_to_crawl}
            
            for future in as_completed(future_to_url):
                current_url = future_to_url[future]
                try:
                    links = future.result()
                except Exception as e:
                    print(f"An error occurred while crawling {current_url}: {e}")
                    continue
                
                print(f"Crawled: {current_url}")
                sitemap.add(current_url)
                to_crawl.update(links - sitemap)

    return sitemap

def save_to_file(sitemap, filename):
    with open(filename, 'w') as f:
        for url in sitemap:
            f.write(f"{url}\n")

if __name__ == "__main__":
    website = input("Enter the URL of the website you want to crawl: ")
    start_url = website
    sitemap = generate_sitemap(start_url)
    save_to_file(sitemap, "sitemap.txt")
    print("Sitemap has been saved to sitemap.txt")