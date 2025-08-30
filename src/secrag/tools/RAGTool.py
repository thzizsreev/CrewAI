import os
from crewai.tools import BaseTool
from typing import List, Dict, Any
from langchain.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceHubEmbeddings
from langchain_core.documents import Document
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define the Hugging Face API key
HUGGINGFACEHUB_API_TOKEN = os.environ.get("HUGGINGFACEHUB_API_TOKEN")

class RAGBuildingTool(BaseTool):
    """
    A tool to build a FAISS vector store from a list of filings
    and save it to the local disk.
    """
    name: str = "RAG Builder"
    description: str = "Builds a FAISS vector store from a list of filing dictionaries."

    def _run(self, filings: List[Dict[str, Any]]) -> str:
        if not filings:
            return "No filings provided to build the RAG system."

        print("Converting filings to LangChain documents...")
        documents = []
        for filing in filings:
            # Join key-value pairs into a single string for the document content
            content = ", ".join([f"{key}: {value}" for key, value in filing.items()])
            # Add metadata from the filing for better retrieval
            metadata = {
                "form_type": filing.get("form_type"),
                "issuer_name": filing.get("issuer", {}).get("name"),
                "reporting_owner": filing.get("reporting_owner", {}).get("name"),
            }
            documents.append(Document(page_content=content, metadata=metadata))

        print("Building RAG in the cloud environment...")
        embeddings = HuggingFaceHubEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN
        )
        
        # Create the vector store from the list of documents
        vector_store = FAISS.from_documents(documents=documents, embedding=embeddings)
        vector_store.save_local("faiss_vector_store")
        
        return "FAISS vector store has been successfully built and saved."
