import requests
import logging
from typing import Dict, Any, List
import json
from pathlib import Path
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LMStudioClient:
    def __init__(
        self,
        base_url: str = "http://localhost:1234",
        model_name: str = "llama-3.2-3b-instruct"
    ):
        self.base_url = base_url.rstrip('/')
        self.model_name = model_name
        self.system_prompt = """You are a medical assistant helping healthcare workers in Uganda.
        Use the provided context from the Uganda Clinical Guidelines 2023 to answer questions.
        Always cite relevant sections of the guidelines.
        Consider resource constraints and local medical practices.
        If unsure, acknowledge limitations and suggest seeking additional medical advice."""
    
    def query(self, question: str, context: str = None) -> Dict[str, Any]:
        """Query LM Studio with context"""
        try:
            messages = self._prepare_messages(question, context)
            
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "messages": messages,
                    "temperature": 0.3, #can adjust if needed
                    "max_tokens": 2000, #can adjust if needed
                    "stream": False
                }
            )
            response.raise_for_status()
            
            result = response.json()
            return {
                "response": result["choices"][0]["message"]["content"],
                "metadata": {
                    "model": self.model_name,
                    "timestamp": time.time()
                }
            }
            
        except Exception as e:
            logger.error(f"Query failed: {str(e)}")
            raise
    
    def _prepare_messages(self, question: str, context: str = None) -> List[Dict]:
        """Prepare messages for LM Studio API"""
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        if context:
            messages.append({
                "role": "system",
                "content": f"Context from guidelines: {context}"
            })
        
        messages.append({"role": "user", "content": question})
        return messages
    
    def test_connection(self) -> bool:
        """Test connection to LM Studio"""
        try:
            response = requests.get(f"{self.base_url}/v1/models")
            response.raise_for_status()
            logger.info("Successfully connected to LM Studio")
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False
