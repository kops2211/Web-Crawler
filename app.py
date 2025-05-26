import streamlit as st
import crawler 
import os
import io
import zipfile        

st.set_page_config(page_title="Web Crawler", layout="centered")
st.title(" Web Crawler ")

target_url = st.text_input("Start URL", crawler.TARGET_URL)
max_pages = st.slider("Max Pages to Crawl", 1, 100, crawler.MAX_CRAWL)
keywords_input = st.text_input("Keywords (comma-separated)", ",".join(crawler.KEYWORDS))

if st.button("Start Crawling"):
    if not target_url.strip():
        st.error("Please enter a valid Start URL.")
    else:
        crawler.TARGET_URL = target_url
    crawler.MAX_CRAWL = max_pages
    crawler.KEYWORDS.clear()
    crawler.KEYWORDS.extend([kw.strip() for kw in keywords_input.split(",") if kw.strip()])

    crawler.high_priority_queue.queue.clear()
    crawler.low_priority_queue.queue.clear()
    crawler.visited_urls.clear()
    crawler.all_links.clear()
    crawler.all_images.clear()
    crawler.keyword_matches.clear()
    crawler.high_priority_queue.put(crawler.TARGET_URL)

    st.info(f"Starting crawl of {crawler.TARGET_URL} ...")
    with st.spinner("Crawling in progress..."):
        crawler.crawl()
        crawler.save_results()
    

    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for filename in ["crawled_links.csv", "crawled_images.csv", "keyword_matches.csv"]:
            file_path = os.path.join(crawler.output_dir, filename)
            if os.path.exists(file_path):
                zip_file.write(file_path, arcname=filename)
    zip_buffer.seek(0)

    st.session_state["zip_file"] = zip_buffer
    st.session_state["results_saved"] = True

    st.success("Crawling completed!")

    if st.session_state.get("results_saved", False):
        st.markdown("#Summary")
        st.write(f"- Total Links: {len(crawler.all_links)}")
        st.write(f"- Total Images: {len(crawler.all_images)}")
        st.write(f"- Pages with Keywords: {len(crawler.keyword_matches)}")

        if st.session_state.get("keyword_matches"):
            with st.expander("View Keyword Matches"):
                for url, keywords in st.session_state["keyword_matches"].items():
                    st.markdown(f"- [{url}]({url}) → `{', '.join(keywords)}`")

        st.markdown("Download All Results")

        if "zip_file" in st.session_state:
            st.download_button(
                label="⬇Download All CSVs as ZIP",
                data=st.session_state["zip_file"],
                file_name="crawler_results.zip",
                mime="application/zip"
            )
