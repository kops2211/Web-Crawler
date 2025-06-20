import streamlit as st
import crawler
import os
import io
import zipfile
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="Web Crawler", layout="centered")
st.title("Web Crawler")

if 'crawl_complete' not in st.session_state:
    st.session_state.crawl_complete = False
    st.session_state.crawl_stats = {
        'pages': 0,
        'images': 0,
        'links': 0,
        'keyword_matches': 0
    }

target_url = st.text_input("Start URL", crawler.TARGET_URL)
max_pages = st.text_input("Max Pages to Crawl", str(crawler.MAX_CRAWL))
keywords_input = st.text_input("Keywords (comma separated)", ",".join(crawler.KEYWORDS))


def reset_crawler():
    crawler.high_priority_queue = crawler.Queue()
    crawler.low_priority_queue = crawler.Queue()
    crawler.visited_urls = set()
    crawler.all_pages = set()
    crawler.all_images = set()
    crawler.all_links_found = set()
    crawler.keyword_matches = {}
    crawler.high_priority_queue.put(crawler.TARGET_URL)


def create_zip():
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename in ['pages.csv', 'images.csv', 'keyword_matches.csv', 'all_links.csv']:
            file_path = os.path.join("crawler_output", filename)
            if os.path.exists(file_path):
                zip_file.write(file_path, arcname=filename)
    zip_buffer.seek(0)
    return zip_buffer


if st.button("Start Crawling", type="primary"):
    if not target_url.strip():
        st.error("Please enter a valid URL")
    else:
        try:
            crawler.TARGET_URL = target_url.strip()
            crawler.MAX_CRAWL = int(max_pages)
            crawler.KEYWORDS = [kw.strip() for kw in keywords_input.split(",") if kw.strip()]

            reset_crawler()

            with st.spinner(f"Crawling {crawler.TARGET_URL}..."):
                crawler.crawl()
                crawler.save_results()

                st.session_state.crawl_complete = True
                st.session_state.zip_file = create_zip()
                st.session_state.crawl_stats = {
                    'pages': len(crawler.all_pages),
                    'images': len(crawler.all_images),
                    'links': len(crawler.all_links_found),
                    'keyword_matches': len(crawler.keyword_matches)
                }

            st.success("Crawling completed!")
        except ValueError:
            st.error("Please enter a valid number for max pages")

if st.session_state.get('crawl_complete', False):
    st.markdown("## Results")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Pages", st.session_state.crawl_stats['pages'])
    with col2:
        st.metric("Images", st.session_state.crawl_stats['images'])
    with col3:
        st.metric("Links Found", st.session_state.crawl_stats['links'])
    with col4:
        st.metric("Keyword Matches", st.session_state.crawl_stats['keyword_matches'])

    if st.session_state.get('zip_file'):
        st.download_button(
            label="Download All Results (ZIP)",
            data=st.session_state.zip_file,
            file_name=f"crawl_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            mime="application/zip",
            key="download_all"
        )

    st.markdown("Or Download Individual Files")

    with st.expander("Keyword Matches", expanded=False):
        if crawler.keyword_matches and os.path.exists("crawler_output/keyword_matches.csv"):
            df_keywords = pd.read_csv("crawler_output/keyword_matches.csv")

            df_display = df_keywords.copy()
            df_display['URL'] = df_display['URL'].apply(
                lambda x: f'<a class="table-link" href="{x}" target="_blank">{x}</a>'
            )

            st.download_button(
                label="Download Keyword Matches",
                data=df_keywords.to_csv(index=False).encode('utf-8'),
                file_name="keyword_matches.csv",
                mime="text/csv"
            )

            st.markdown(
                df_display.to_html(escape=False, index=False),
                unsafe_allow_html=True
            )

    with st.expander("Pages", expanded=False):
        if os.path.exists("crawler_output/pages.csv"):
            df_pages = pd.read_csv("crawler_output/pages.csv")

            df_display = df_pages.copy()
            df_display['URL'] = df_display['URL'].apply(
                lambda x: f'<a class="table-link" href="{x}" target="_blank"> {x}</a>'
            )

            st.download_button(
                label="Download Pages Data",
                data=df_pages.to_csv(index=False).encode('utf-8'),
                file_name="pages.csv",
                mime="text/csv"
            )

            st.markdown(
                df_display.to_html(escape=False, index=False),
                unsafe_allow_html=True
            )

    if os.path.exists("crawler_output/images.csv"):
        with st.expander(" Images", expanded=False):
            df_images = pd.read_csv("crawler_output/images.csv")

            df_display = df_images.copy()
            df_display['Image URL'] = df_display['Image URL'].apply(
                lambda x: f'<a class="table-link" href="{x}" target="_blank"> {x}</a>'
            )
            df_display['Source URL'] = df_display['Source URL'].apply(
                lambda x: f'<a class="table-link" href="{x}" target="_blank"> {x}</a>'
            )

            st.download_button(
                label="Download Images Data",
                data=df_images.to_csv(index=False).encode('utf-8'),
                file_name="images.csv",
                mime="text/csv"
            )

            st.markdown(
                df_display.to_html(escape=False, index=False),
                unsafe_allow_html=True
            )

    if os.path.exists("crawler_output/all_links.csv"):
        with st.expander("All Links", expanded=False):
            df_links = pd.read_csv("crawler_output/all_links.csv")

            df_display = df_links.copy()
            df_display['Link URL'] = df_display['Link URL'].apply(
                lambda x: f'<a class="table-link" href="{x}" target="_blank"> {x}</a>'
            )
            df_display['Source URL'] = df_display['Source URL'].apply(
                lambda x: f'<a class="table-link" href="{x}" target="_blank"> {x}</a>'
            )

            st.download_button(
                label="Download Links Data",
                data=df_links.to_csv(index=False).encode('utf-8'),
                file_name="all_links.csv",
                mime="text/csv"
            )

            st.markdown(
                df_display.to_html(escape=False, index=False),
                unsafe_allow_html=True
            )

# Inject CSS styling
st.markdown("""
 <style>
    div[data-testid="stExpander"] {
        border: 1px solid rgba(49, 51, 63, 0.2);
        border-radius: 6px;
        overflow: hidden;
        margin-bottom: 1rem;
    }
    div[data-testid="stExpander"] > div:first-child {
        background-color: #f0f2f6;
        padding: 10px 14px;
        font-weight: 600;
    }
    div[data-testid="stExpander"] > div:nth-child(2) {
        padding: 14px;
    }
    table {
        width: 100% !important;
        border-collapse: collapse;
        table-layout: fixed;
        font-size: 13px;
        margin-top: 10px;
        word-wrap: break-word;
    }
    th, td {
        padding: 10px 8px;
        text-align: left;
        vertical-align: top;
        border-bottom: 1px solid #e0e0e0;
        word-break: break-word;
        white-space: normal;
    }
    th {
        background-color: #f9fafc;
        font-weight: 600;
    }
    tr:hover {
        background-color: #f6f8fa;
    }
    a {
        color: #1a73e8 !important;
        text-decoration: none !important;
    }
    a:hover {
        text-decoration: underline !important;
    }
</style>
""", unsafe_allow_html=True)
