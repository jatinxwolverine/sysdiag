import csv
import time
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 1. Scraping Configuration & Best Practices
BASE_URL = "http://quotes.toscrape.com"
OUTPUT_FILE = "quotes.csv"

# Implement retry logic to handle rate limiting or temporary network issues
retry_strategy = Retry(
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
    backoff_factor=1,
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)

# Custom headers to mimic a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


def scrape_quotes():
    quotes_data = []
    page = 1
    has_next = True

    print("Starting scraping process...")

    while has_next:
        url = f"{BASE_URL}/page/{page}/"
        print(f"Scraping {url}...")

        try:
            response = http.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        quote_elements = soup.find_all("div", class_="quote")

        if not quote_elements:
            break

        for element in quote_elements:
            text = element.find("span", class_="text").get_text(strip=True)
            author = element.find("small", class_="author").get_text(strip=True)
            tags = [
                tag.get_text(strip=True)
                for tag in element.find_all("a", class_="tag")
            ]

            quotes_data.append(
                {"text": text, "author": author, "tags": ", ".join(tags)}
            )

        # Rate limiting: polite pause between pages
        time.sleep(1)

        # Check for next page
        next_button = soup.find("li", class_="next")
        if next_button:
            page += 1
        else:
            has_next = False

    print("Scraping completed.")
    return quotes_data


def save_to_csv(data, filename):
    keys = ["text", "author", "tags"]

    print(f"Saving data to {filename}...")
    with open(filename, "w", newline="", encoding="utf-8") as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

    print("Data saved successfully.")


def print_summary(data):
    print("\n--- Scraping Summary ---")
    print(f"Total Quotes Extracted: {len(data)}")

    authors = [item["author"] for item in data]
    unique_authors = len(set(authors))
    print(f"Unique Authors: {unique_authors}")

    if data:
        tag_counts = {}
        for item in data:
            if item["tags"]:
                for tag in item["tags"].split(", "):
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1

        if tag_counts:
            most_common_tag = max(tag_counts, key=tag_counts.get)
            print(f"Most Common Tag: {most_common_tag}")
    print("------------------------\n")


if __name__ == "__main__":
    extracted_data = scrape_quotes()
    if extracted_data:
        save_to_csv(extracted_data, OUTPUT_FILE)
        print_summary(extracted_data)