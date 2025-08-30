import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from typing import List, Dict, Any
from ...tools.RAGTool import RAGBuildingTool

# from my_project.tools.parse_sec_filings import SECFilingParser
# from my_project.tools.rss import RSSFetcher

# Load environment variables for API keys
load_dotenv()

class RAGBuilderCrew:

    def __init__(self, filing_text: List[Dict[str, Any]]):
        self.filing_text = filing_text
        
        # Initialize a local LLM using Ollama
        # You must have Ollama running with the 'llama3' model downloaded
        self.llm = LLM(
            model="ollama/llama3",
            base_url="http://localhost:11434"
        )
        
        # Initialize a local embedding model from Hugging Face
        # This will download the model the first time it's run
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

    def kickoff(self):
        # Agents
        data_ingestor = Agent(
            role='Data Ingestor',
            goal='Process all provided SEC filings and prepare them for a RAG system.',
            backstory="""
                You are a highly efficient data processor. Your sole responsibility is to
                convert a Python list of dictionaries into a structured format suitable for
                a knowledge base.
            """,
            llm=self.llm,
            verbose=True,
            tools=[RAGBuildingTool()]
        )

        # Tasks
        ingest_filings_task = Task(
            description='Take the provided filing data and create a unified knowledge base.',
            expected_output='A confirmation message that the knowledge base has been created.',
            agent=data_ingestor
        )

        # Crew
        rag_building_crew = Crew(
            agents=[data_ingestor],
            tasks=[ingest_filings_task],
            process=Process.sequential,
            verbose=True
        )
        
        # Execute the task without explicit inputs, the agent will use its context
        rag_building_crew.kickoff()
        
        # Manually create the RAG system after the task is done
        documents = [
            Document(page_content=str(filing)) for filing in self.filing_text
        ]
        
        # Create and save the FAISS vector store using the local embedding model
        vector_store = FAISS.from_documents(documents, self.embeddings)
        vector_store.save_local("faiss_vector_store")
        
        return "RAG system has been successfully built and saved."
