from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

from rss import RSSFetchers
from parse_sec_filings import SECFilingParser

class MyCustomToolInput(BaseModel):
    """Input schema for MyCustomTool."""
    argument: str = Field(..., description="Description of the argument.")

class MyCustomTool(BaseTool):
    name: str = "Name of my tool"
    description: str = (
        "Clear description for what this tool is useful for, your agent will need this information to use it."
    )
    args_schema: Type[BaseModel] = MyCustomToolInput

    def _run(self, argument: str) -> str:
        # Example: Use fetch_rss to get filings, then parse one with SECFilingParser
        try:
            feed = fetch_rss(0)
            if not feed:
                return "No filings found."
            first_entry = feed[0]
            filing_url = first_entry.link
            parser = SECFilingParser()
            # Download and parse the filing
            filing_text = parser.collect_txt(filing_url)
            parsed = parser.parse_sec_filing(filing_text)
            return f"Parsed filing: {parsed}"
        except Exception as e:
            return f"Error: {e}"