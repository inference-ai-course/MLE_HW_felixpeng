import requests
import feedparser
import trafilatura
from PIL import Image
import pytesseract
import json
import os
import time

#arXiv API, https://info.arxiv.org/help/api/user-manual.html#_preface
#Electrical Engineering and Systems Science, Systems and Control, Latest 200 papers
#Returns feedparser objects
def fetch_arxiv_entries(category="eess.SY", max_results=200):
    base_url = "http://export.arxiv.org/api/query?"
    query = f"search_query=cat:{category}&start=0&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"
    response = requests.get(base_url + query)
    return feedparser.parse(response.text).entries

#Takes in url of abstract page
#Cleans using trafilatura, returns the context
def clean_abs_page(url):
    try:
        html = requests.get(url).text
        cleaned = trafilatura.extract(html)
        return cleaned if cleaned else ""
    except Exception as e:
        print(f"[!] Failed to clean {url}: {e}")
        return ""

#Takes in filepath of image and does OCR using tesseract, returns as a string 
#PSM 1 is slower but better at recognizing tables
def extract_abstract_from_image(image_path):
    img = Image.open(image_path)
    return pytesseract.image_to_string(img, config="--psm 1")


#Formats arXiv entry into dictionary with fields
def parse_entry(entry, cleaned_abstract=None):
    return {
        "url": entry.link,
        "title": entry.title,
        "abstract": cleaned_abstract.strip(),  # use cleaned value here
        "authors": [author.name for author in entry.authors],
        "date": entry.published
    }

#Saves a list of paper dictionaries as a JSON file
def save_json(data, filename="arxiv_clean.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

#Keep popping entries until under 1 MB
def reduce_size(entries, max_bytes=1_000_000):
    while True:
        output = json.dumps(entries, ensure_ascii=False)
        if len(output.encode('utf-8')) <= max_bytes:
            return entries
        entries.pop()


def main():
    """
    Main routine to fetch, clean, format, and save arXiv metadata.
    """
    category = "eess.SY"
    print(f"Fetching latest papers from arXiv category: {category}")
    entries = fetch_arxiv_entries(category=category, max_results=200)

    papers = []
    for i, entry in enumerate(entries):
        print(f"[{i+1}] Processing: {entry.title[:60]}...")
        cleaned = clean_abs_page(entry.link)
        paper = parse_entry(entry, cleaned)
        papers.append(paper)
        time.sleep(15)  # crawl delay set by arXiv robots.txt

    print(f"Reducing dataset to ≤1MB if necessary...")
    trimmed = reduce_size(papers, max_bytes=1_000_000)

    save_json(trimmed, filename="arxiv_clean.json")

main()