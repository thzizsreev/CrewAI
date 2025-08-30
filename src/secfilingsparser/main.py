#!/usr/bin/env python
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import os

from crewai.flow import Flow, listen, start

from .crews.poem_crew.FinancialFilingsCrew import FinancialFilingsCrew
from .rss import RSSFetcher
from .parse_sec_filings import SECFilingParser

class PoemState(BaseModel):
    feed_entries: List[Dict[str, Any]] = []
    analysis: str = ""
    filing_text: List[Dict[str, Any]] = []

class PoemFlow(Flow[PoemState]):

    @start()
    def process_filings(self):
        print("Generating filings")
        fetcher = RSSFetcher(
            base_url="https://www.sec.gov/cgi-bin/browse-edgar",
            headers={"User-Agent": "sreeev Test@gmail.com"}
        )
        print("Fetching RSS feed entries...")
        feed_entries = fetcher.main()
        parser = SECFilingParser()
        try:
            self.state.filing_text = parser.process_filings(feed_entries)
        except Exception as e:
            print(f"Error parsing filings: {e}")
            self.state.filing_text = []

    @listen(process_filings)
    def analyze_and_summarize(self):
        print("Agent working on analysis and summarization")
        crew = FinancialFilingsCrew()
        all_analysis = ""
        # Process each filing individually to avoid context window issues
        for filing in self.state.filing_text:
            inputs = {
                "filings_text": filing  # Pass one filing at a time
            }
            # Correctly unpacks the single string output
            analysis = str(crew.crew().kickoff(inputs=inputs))
            all_analysis += analysis[1:] + "\n\n"
        
        # This is where the output is written to a new file
        output_file_path = "summary.md"
        with open(output_file_path, "w") as f:
            f.write(all_analysis)
        
        self.state.analysis = all_analysis
        print(f"Final analysis written to '{output_file_path}'.")

def kickoff():
    poem_flow = PoemFlow()
    poem_flow.kickoff()
    
def plot():
    poem_flow = PoemFlow()
    poem_flow.plot()

if __name__ == "__main__":
    kickoff()
