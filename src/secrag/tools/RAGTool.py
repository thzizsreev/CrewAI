import os
from crewai.tools import BaseTool
from typing import List, Dict, Any

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class RAGBuildingTool(BaseTool):
    """
    A tool to build a FAISS vector store from a list of filings
    and save it to the local disk.
    """
    name: str = "RAG Builder"
    description: str = "Builds a FAISS vector store from a list of filing dictionaries."

    def _run(self, filings: List[Dict[str, Any]]) -> str:
        try:
            if not filings:
                return "No filings provided to build the RAG system."

            print("Converting filings to LangChain documents...")
            documents = []
            for filing in filings:
                # Join key-value pairs into a single string for the document content
                content = ", ".join([f"{key}: {value}" for key, value in filing.items()])
                # Add metadata from the filing for better retrieval
                metadata = {
                    "form_type": filing.get("form_type", ""),
                    "issuer_name": filing.get("issuer", {}).get("name", "") if isinstance(filing.get("issuer"), dict) else "",
                    "reporting_owner": filing.get("reporting_owner", {}).get("name", "") if isinstance(filing.get("reporting_owner"), dict) else "",
                }
                documents.append(Document(page_content=content, metadata=metadata))

            print("Building RAG with local embeddings...")
            # Use local HuggingFace embeddings instead of API-based
            # This will download the model on first use and cache it locally
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},  # Use CPU, change to 'cuda' if you have GPU
                encode_kwargs={'normalize_embeddings': False}
            )
            
            # Create the vector store from the list of documents
            print(f"Creating vector store from {len(documents)} documents...")
            vector_store = FAISS.from_documents(documents=documents, embedding=embeddings)
            
            # Save the vector store locally
            print("Saving vector store to disk...")
            vector_store.save_local("faiss_vector_store")
            
            return f"FAISS vector store has been successfully built with {len(documents)} documents and saved to 'faiss_vector_store'."
        
        except Exception as e:
            return f"Error building RAG system: {str(e)}"