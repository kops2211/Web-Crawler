import requests
from bs4 import BeautifulSoup
import re, os
from urllib.parse import urljoin, urlparse
from tenacity import retry, stop_after_attempt, wait_exponential
from queue import Queue
import csv
import time
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin

TARGET_URL = "http://books.toscrape.com"  
MAX_CRAWL = 5  
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
DELAY = 1  
KEYWORDS = [] 
rp = RobotFileParser()

def load_robots_txt(base_url):

    rp.set_url(urljoin(base_url, '/robots.txt'))
    rp.read()
    return rp


def can_fetch(url):
    return rp.can_fetch(USER_AGENT, url)
 

high_priority_queue = Queue()
low_priority_queue = Queue()
visited_urls = set()
all_links = set()
all_images = set()
keyword_matches = {}  


high_priority_queue.put(TARGET_URL)


session = requests.Session()
session.headers.update({'User-Agent': USER_AGENT})



@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def fetch_url(url):
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        raise
def is_same_domain(url, base_url):
    return urlparse(url).netloc == urlparse(base_url).netloc
def normalize_url(url):
    parsed = urlparse(url)
    return parsed.scheme + "://" + parsed.netloc + parsed.path
def check_keywords(content):
    content_lower = content.lower()
    matches = [kw for kw in KEYWORDS if kw.lower() in content_lower]
    return matches if matches else None
def extract_links_and_images(soup, base_url):
    links = set()
    images = set()
    

    for link in soup.find_all('a', href=True):
        url = link['href'].strip()
        if not url or url.startswith('javascript:'):
            continue
        
        
        absolute_url = urljoin(base_url, url)
        absolute_url = normalize_url(absolute_url)
        
    
        if is_same_domain(absolute_url, base_url):
            links.add(absolute_url)
    
    
    for img in soup.find_all('img', src=True):
        img_url = img['src'].strip()
        if not img_url:
            continue
        
        
        absolute_img_url = urljoin(base_url, img_url)
        images.add(absolute_img_url)
    
    return links, images
def crawl():
    if not TARGET_URL:
        print("No target URL set for crawling.")
        return
    
    rp = load_robots_txt(TARGET_URL)

    crawl_count = 0
    
    while (not high_priority_queue.empty() or not low_priority_queue.empty()) and crawl_count < MAX_CRAWL:
        if not high_priority_queue.empty():
            current_url = high_priority_queue.get()
        else:
            current_url = low_priority_queue.get()
            
        if current_url in visited_urls:
            continue
            
        print(f"Crawling {current_url} ({crawl_count + 1}/{MAX_CRAWL})")
        
        try:
            response = fetch_url(current_url)
            visited_urls.add(current_url)
        
            soup = BeautifulSoup(response.content, 'html.parser')
            
            text_content = soup.get_text()
            matched_keywords = check_keywords(text_content)
            if matched_keywords:
                keyword_matches[current_url] = matched_keywords
                print(f"Found keywords {matched_keywords} in {current_url}")
            
            new_links, new_images = extract_links_and_images(soup, current_url)
            
            all_images.update(new_images)
            
            for link in new_links:
                if link not in visited_urls and link not in all_links:
                    all_links.add(link)
            
                    if any(re.search(rf'/{kw}/', link, re.I) for kw in KEYWORDS):
                        high_priority_queue.put(link)
                    else:
                        low_priority_queue.put(link)
            
            time.sleep(DELAY)
            
            crawl_count += 1
            
        except Exception as e:
            print(f"Failed to process {current_url}: {str(e)}")
            continue
output_dir = "crawler_output"
os.makedirs(output_dir, exist_ok=True)
def save_results():
    with open(os.path.join(output_dir, 'crawled_links.csv'), 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['URL'])
        for link in sorted(all_links):
            writer.writerow([link])
    
    with open(os.path.join(output_dir, 'crawled_images.csv'), 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Image URL'])
        for img in sorted(all_images):
            writer.writerow([img])
    
    with open(os.path.join(output_dir, 'keyword_matches.csv'), 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['URL', 'Matched Keywords'])
        for url, keywords in keyword_matches.items():
            writer.writerow([url, ', '.join(keywords)])
if __name__ == '__main__':
    print(f"Starting crawl of {TARGET_URL} (max {MAX_CRAWL} pages)")
    print(f"Searching for keywords: {', '.join(KEYWORDS)}")
    crawl()
    save_results()
    print(f"Crawl completed. Found:")
    print(f"- {len(all_links)} total links")
    print(f"- {len(all_images)} total images")
    print(f"- {len(keyword_matches)} pages containing keywords")
   





