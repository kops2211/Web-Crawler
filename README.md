Web Crawler App

A Python-based web crawler with a Streamlit user interface. It crawls websites, extracts links and images, and detects keyword matches in web page content. Results are saved as CSV files and available for download.

#Features
- Crawl a target website up to a specified number of pages
- Extract:
  - Internal links
  - Image URLs
  - Keyword matches
- Download results as CSV files
- User-friendly Streamlit interface

#Technologies Used
- Python 3.10+
- Streamlit
- BeautifulSoup
- Requests
- Tenacity
- CSV

#Setup Instructions
1. *Clone the Repository*
```bash
git clone https://github.com/yourusername/web-crawler.git
cd web-crawler
Install Requirements

bash
Copy
Edit
pip install -r requirements.txt
Run the App

bash
Copy
Edit
streamlit run app.py
Open in Browser

Navigate to http://localhost:8501 in your browser to use the app.

#How to Use
1. Enter a target URL (e.g., http://books.toscrape.com).
2. Enter max pages to crawl.
3. Optionally enter keywords to search in page content.
4. Click Start Crawling.
5. Download CSV results after completion.
Output Files(Saved automatically in crawler_output in zip):
-crawled_links.csv
-crawled_images.csv
-keyword_matches.csv

License
MIT License
