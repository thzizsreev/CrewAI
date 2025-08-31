import requests, datetime, json
import feedparser
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
import os

class RSSFetcher():
    def __init__(self, base_url, headers):
        self.base_url = base_url
        self.headers = headers
        self.counter = 0

    def fetch_rss(self, start):
        url = f"{self.base_url}?action=getcurrent&CIK=&type=4&company=&dateb=&owner=only&start={start}&count=100&output=atom"
        resp = requests.get(url, headers=self.headers)
        feed = feedparser.parse(resp.text)
        # print(feed.entries)
        return feed.entries

    def is_recent(self, entry, hours=48):
        # Parse RFC3339 timestamp like "2025-08-25T11:05:32-04:00"
        updated_time = date_parser.parse(entry.updated)
        
        now = datetime.datetime.now(datetime.timezone.utc)
        age = now - updated_time
        
        return age.total_seconds() <= hours * 3600, updated_time.isoformat()

    def get_txt_link(self, index_url):
        r = requests.get(index_url, headers=self.headers)
        soup = BeautifulSoup(r.text, "html.parser")
        for row in soup.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) >= 3:
                desc = cells[1].get_text(strip=True).lower()
                link = cells[2].find("a")["href"]
                print(f"DESC: {desc} | LINK: {link}")
                if "complete submission text file" in desc:
                    return "https://www.sec.gov" + link
        return None

    def parse_txt(self, txt_url):
        r = requests.get(txt_url, headers=self.headers)
        text = r.text
        
        # TODO: parse <DOCUMENT> blocks and extract insider trading info
        # For now, just return stub
        return {"filing_url": txt_url, "raw_text_length": len(text)}

    def collect_filings(self, feed):
        # global counter
        
        filings = []
        for entry in feed:
            
            temp = self.is_recent(entry)
            if not temp[0]: 
                print(f"Skipping older entry: {temp[1]}, THE END")
                return filings, False
            
            index_url = entry.link
            txt_url = self.get_txt_link(index_url)
            if txt_url:
                filing_data = {}
                filing_data["counter"] = self.counter
                self.counter = self.counter + 1
                filing_data["title"] = entry.title
                filing_data["link"] = txt_url
                filing_data["date"] = temp[1]
                filings.append(filing_data)

            if self.counter >= 20:  # temp limit for testing
                break

        return filings, True

    def main(self):
        
        filings = []
        start = 0
        print("Starting")

        while True:
            print(f"Fetching batch starting at {start}...")
            feed = self.fetch_rss(start)
            batch, keep_going = self.collect_filings(feed)

            filings.extend(batch)   # ✅ keep everything, don’t overwrite

            if not keep_going:      # stop if older than 48h encountered
                break

            if start != 0:          #temp
                break
            start += 100            # paginate

        return filings

