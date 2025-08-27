from crewai.tools import BaseTool
from typing import Type, List
from pydantic import BaseModel, Field
import json
import os

# Import the classes from your other files
from .rss import RSSFetcher
from .parse_sec_filings import SECFilingParser


output_dir = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "contents_urls.json")
output_path2 = os.path.join(output_dir, "contents.json")
# Define the input schema for the RSS fetching tool
class RSSFetcherToolInput(BaseModel):
    start_index: int = Field(..., description="The starting index for fetching RSS feed entries.")

class RSSFetcherTool(BaseTool):
    name: str = "SEC RSS Feed Fetcher"
    description: str = "Fetches recent SEC filing entries from an RSS feed. Use this to get a list of recent filings."
    args_schema: Type[BaseModel] = RSSFetcherToolInput

    def _run(self):
        # Initialize your RSSFetcher
        fetcher = RSSFetcher(
            base_url="https://www.sec.gov/cgi-bin/browse-edgar",
            headers={"User-Agent": "MyApp/1.0"}
        )
        # Fetch the feed entries
        feed_entries = fetcher.main()
        # Return a list of dictionaries with relevant info

        
        with open(output_path, "w", encoding="utf8") as f:
            json.dump(feed_entries, f, indent=2)
            # write your data
        return feed_entries

# Define the input schema for the SEC parsing tool
class SECFilingParserToolInput(BaseModel):
    filing_url: str = Field(..., description="The URL of the SEC filing's full text file to be parsed.")

class SECFilingParserTool(BaseTool):
    name: str = "SEC Filing Parser"
    description: str = "Downloads and parses the text content of a single SEC filing from its URL. It extracts key information and saves it to 'contents_urls.txt'."
    args_schema: Type[BaseModel] = SECFilingParserToolInput

    def _run(self):
        parser = SECFilingParser()
        with open(output_path, "r", encoding="utf8") as f:
            data = json.load(f)
        try:
            # Download the filing text
            filing_text = parser.process_filings(data)
            # Parse it
            with open(output_path2, "w", encoding="utf8") as f:
                json.dump(filing_text, f, indent=2)
            
            # The parser already writes to a file, so we can return a success message
            # with the path to the output.
            return filing_text
        except Exception as e:
            return f"Error parsing filing from {filing_url}: {e}"