#!/usr/bin/env python
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import os

from crewai.flow import Flow, listen, start
from .crews.ragbuildercrew.ragbuildercrew import RAGBuilderCrew
from .crews.poem_crew.FinancialFilingsCrew import FinancialFilingsCrew
from .rss import RSSFetcher
from .parse_sec_filings import SECFilingParser

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA

from .crews.ragbuildercrew.ragbuildercrew import RAGBuilderCrew
#from .report_generator_crew import ReportGeneratorCrew


class PoemState(BaseModel):
    feed_entries: List[Dict[str, Any]] = []
    analysis: str = ""
    filing_text: List[Dict[str, Any]] = []
    rag_builder_output: str = ""
    final_report: str = ""


def test_rag_query(query: str):
    """
    Function to test the RAG by loading the saved vector store
    and running a query against it.
    """
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        vector_store = FAISS.load_local(
            "faiss_vector_store", embeddings, allow_dangerous_deserialization=True
        )
        
        retriever = vector_store.as_retriever()
        
        # You can use a simple, non-agent LLM for this quick test
        
        llm = Ollama(model="llama3", base_url="http://localhost:11434")

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever
        )
        
        result = qa_chain.run(query)
        print("\n--- RAG Test Query Result ---")
        print(result)
        #return result
    except Exception as e:
        print(f"Error during RAG test: {e}")
        return None

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
    def BuildRAG(self):
        print("Building RAG system")
        
        crew = RAGBuilderCrew(self.state.filing_text)
        crew.kickoff()

    @listen(BuildRAG)
    def test_rag(self):
        # A simple test query to verify the RAG is functional
        query = "What is the form type for the filing?"
        test_rag_query(query)

    # @listen(BuildRAG)
    # def analyze_and_summarize(self):
    #     print("Agent working on analysis and summarization")
    #     crew = FinancialFilingsCrew()
    #     all_analysis = ""
    #     # Process each filing individually to avoid context window issues
    #     for filing in self.state.filing_text:
    #         inputs = {
    #             "filings_text": filing  # Pass one filing at a time
    #         }
    #         # Correctly unpacks the single string output
    #         analysis = str(crew.crew().kickoff(inputs=inputs))
    #         all_analysis += analysis[1:] + "\n\n"
        
    #     # This is where the output is written to a new file
    #     output_file_path = "summary.md"
    #     with open(output_file_path, "w") as f:
    #         f.write(all_analysis)
        
    #     self.state.analysis = all_analysis
    #     print(f"Final analysis written to '{output_file_path}'.")

def kickoff():
    poem_flow = PoemFlow()
    poem_flow.kickoff()
    
def plot():
    poem_flow = PoemFlow()
    poem_flow.plot()

if __name__ == "__main__":
    kickoff()
