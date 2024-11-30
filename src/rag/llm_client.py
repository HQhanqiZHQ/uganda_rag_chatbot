# src/rag/llm_client.py
import requests
import time
from typing import Dict, Any, List, Optional
from openai import OpenAI
import chromadb
from chromadb.config import Settings
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import settings
from src.logger import setup_logger
from src.prompts import SYSTEM_PROMPT

logger = setup_logger("llm_client")

class LLMClient:
    def __init__(
        self,
        model_type: str = "lmstudio",
        model_name: str = "llama-3.2-3b-instruct",
        api_key: Optional[str] = settings.OPENAI_API_KEY,
        base_url: str = settings.LM_STUDIO_URL,
        chroma_host: str = settings.CHROMA_HOST,
        chroma_port: int = settings.CHROMA_PORT,
        data_path: str = settings.DATA_PATH,
        reset_collection: bool = False
    ):
        self.model_type = model_type
        self.model_name = model_name
        self.base_url = base_url.rstrip('/')
        self.data_path = Path(data_path)
        
        # Initialize OpenAI client if needed for GPT-4 queries
        if api_key:
            self.openai_client = OpenAI(api_key=api_key)
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.HttpClient(
            host=chroma_host,
            port=chroma_port,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Use same collection name for both models since using same embeddings
        collection_name = "medical_guidelines_nomic"
        try:
            # Try to get existing collection first
            self.collection = self.chroma_client.get_collection(name=collection_name)
            logger.info(f"Using existing collection: {collection_name}")
            logger.info(f"Collection has {self.collection.count()} documents")
        except:
            # Create new collection if it doesn't exist
            self.collection = self.chroma_client.create_collection(
                name=collection_name,
                get_or_create=True
            )
            logger.info(f"Created new collection: {collection_name}")
            
            # Only load documents for new collections
            if self.data_path.exists():
                logger.info("Starting document loading...")
                self.add_documents(str(self.data_path))
            else:
                logger.error(f"Data path not found: {self.data_path}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_embeddings(self, text: str) -> List[float]:
        """Get embeddings using nomic-embed-text-v1.5 consistently"""
        try:
            logger.info(f"Getting embedding for text of length {len(text)}")
            response = requests.post(
                f"{self.base_url}/v1/embeddings",
                json={
                    "model": "nomic-embed-text-v1.5",
                    "input": text
                }
            )
            response.raise_for_status()
            embedding = response.json()["data"][0]["embedding"]
            logger.info("Successfully got embedding")
            return embedding
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            raise
        
    def add_documents(self, file_path: str):
        """Load and index documents with deduplication and better section preservation"""
        try:
            logger.info(f"Starting document processing from: {file_path}")
            
            # Check if file exists
            if not Path(file_path).exists():
                logger.error(f"File not found: {file_path}")
                return
                
            # Get existing documents
            existing_docs = set()
            if self.collection.count() > 0:
                existing_docs = set(self.collection.get()["documents"])
                logger.info(f"Found {len(existing_docs)} existing documents")
            
            # Read and chunk new documents
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
                logger.info(f"Read {len(text)} bytes from file")
            
            # Initialize variables for chunking
            chunks = []
            current_section = ""
            current_subsection = ""
            current_chunk = []
            chunk_size = 0
            MAX_CHUNK_SIZE = 1000  # Adjust as needed
            
            # Process line by line
            lines = text.split('\n')
            logger.info(f"Processing {len(lines)} lines")
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line:
                    continue
                    
                # Detect section headers
                if line.startswith('# '):  # Main section
                    logger.debug(f"Found main section at line {line_num}: {line[:50]}...")
                    if current_chunk:
                        chunk_text = f"{current_section}\n{current_subsection}\n{''.join(current_chunk)}"
                        if chunk_text not in existing_docs:
                            chunks.append(chunk_text)
                            logger.debug(f"Added chunk with section: {current_section[:50]}...")
                    current_section = line
                    current_subsection = ""
                    current_chunk = []
                    chunk_size = 0
                elif line.startswith('## '):  # Subsection
                    logger.debug(f"Found subsection at line {line_num}: {line[:50]}...")
                    if current_chunk:
                        chunk_text = f"{current_section}\n{current_subsection}\n{''.join(current_chunk)}"
                        if chunk_text not in existing_docs:
                            chunks.append(chunk_text)
                            logger.debug(f"Added chunk with subsection: {current_subsection[:50]}...")
                    current_subsection = line
                    current_chunk = []
                    chunk_size = 0
                else:
                    # Add line to current chunk
                    current_chunk.append(line + '\n')
                    chunk_size += len(line)
                    
                    # If chunk size exceeds limit, save it and start new chunk
                    if chunk_size >= MAX_CHUNK_SIZE:
                        chunk_text = f"{current_section}\n{current_subsection}\n{''.join(current_chunk)}"
                        if chunk_text not in existing_docs:
                            chunks.append(chunk_text)
                            logger.debug(f"Added chunk due to size limit: {chunk_size} bytes")
                        current_chunk = []
                        chunk_size = 0
            
            # Add final chunk if exists
            if current_chunk:
                chunk_text = f"{current_section}\n{current_subsection}\n{''.join(current_chunk)}"
                if chunk_text not in existing_docs:
                    chunks.append(chunk_text)
                    logger.debug("Added final chunk")
            
            logger.info(f"Created {len(chunks)} chunks for processing")
            
            if not chunks:
                logger.info("No new documents to add")
                return
            
            # Generate embeddings for new chunks
            embeddings = []
            for i, chunk in enumerate(chunks, 1):
                try:
                    logger.debug(f"Generating embedding for chunk {i}/{len(chunks)}")
                    embedding = self.get_embeddings(chunk)
                    embeddings.append(embedding)
                    logger.debug(f"Successfully generated embedding {i}/{len(chunks)}")
                except Exception as e:
                    logger.error(f"Failed to generate embedding for chunk {i}: {str(e)}")
                    continue
            
            if not embeddings:
                logger.error("No embeddings were generated successfully")
                return
                
            logger.info(f"Generated {len(embeddings)} embeddings successfully")
            
            # Add new documents to collection
            self.collection.add(
                embeddings=embeddings,
                documents=chunks,
                ids=[f"doc_{i}" for i in range(len(chunks))]
            )
            logger.info(f"Added {len(chunks)} new documents to ChromaDB")
            
        except Exception as e:
            logger.error(f"Failed to add documents: {str(e)}")
            logger.exception("Detailed error trace:")
            raise
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def query(
        self,
        question: str,
        temperature: float = 0.3,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """Query with retry logic"""
        try:
            # Get relevant context
            results = self.collection.query(
                query_texts=[question],
                n_results=4 # increase number of context chunks, tried 2, not so good.
            )
            
            context = "\n".join(results['documents'][0]) if results['documents'] else ""
            
            # Prepare messages
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "system", "content": f"Context:\n{context}"},
                {"role": "user", "content": question}
            ]
            
            # Get completion based on model type
            if self.model_type == "lmstudio":
                response = requests.post(
                    f"{self.base_url}/v1/chat/completions",
                    json={
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "stream": False
                    }
                )
                response.raise_for_status()
                result = response.json()
                content = result["choices"][0]["message"]["content"]
            else:
                response = self.openai_client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                content = response.choices[0].message.content
            
            return {
                "response": content,
                "metadata": {
                    "model": self.model_type,
                    "temperature": temperature,
                    "timestamp": time.time(),
                    "context_used": bool(context)
                }
            }
            
        except Exception as e:
            logger.error(f"Query failed: {str(e)}")
            raise
