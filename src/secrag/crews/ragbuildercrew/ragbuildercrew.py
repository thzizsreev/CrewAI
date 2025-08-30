import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from typing import List, Dict, Any
from ...tools.RAGTool import RAGBuildingTool

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
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cuda'},  # Use CPU, change to 'cuda' if you have GPU
            encode_kwargs={'normalize_embeddings': False}
        )

    def kickoff(self):
        # Initialize the RAG Building Tool
        rag_tool = RAGBuildingTool()
        
        # Agents
        data_ingestor = Agent(
            role='Data Ingestor',
            goal='Process all provided SEC filings and prepare them for a RAG system.',
            backstory="""
                You are a highly efficient data processor. Your sole responsibility is to
                convert a Python list of dictionaries into a structured format suitable for
                a knowledge base. You must use the RAG Builder tool to process the filings.
            """,
            llm=self.llm,
            verbose=True,
            tools=[rag_tool]
        )

        # Tasks - Pass the filing data directly in the task description
        ingest_filings_task = Task(
            description=f'''Take the provided filing data and create a unified knowledge base.
            
            Here is the filing data to process:
            {self.filing_text}
            
            Use the RAG Builder tool with this data.''',
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
        
        # Execute the crew
        result = rag_building_crew.kickoff()
        
        # If the tool didn't work, create the RAG system manually as a fallback
        if "Error" in str(result) or "failed" in str(result).lower():
            print("Tool execution failed, creating RAG system manually...")
            documents = [
                Document(page_content=str(filing)) for filing in self.filing_text
            ]
            
            # Create and save the FAISS vector store using the local embedding model
            vector_store = FAISS.from_documents(documents, self.embeddings)
            vector_store.save_local("faiss_vector_store")
            
            return "RAG system has been successfully built and saved (manual fallback)."
        
        return result