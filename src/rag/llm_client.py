import requests
import logging
from openai import OpenAI
from typing import Dict, Any, List, Optional
import json
from pathlib import Path
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(
        self,
        model_type: str = "lmstudio",  # "lmstudio" or "openai"
        model_name: str = "llama-3.2-3b-instruct",
        api_key: Optional[str] = None,
        base_url: str = "http://localhost:1234"
    ):
        self.model_type = model_type
        self.model_name = model_name
        self.base_url = base_url.rstrip('/')
        
        # Initialize OpenAI client if needed
        if model_type == "openai":
            if not api_key:
                raise ValueError("OpenAI API key is required")
            self.openai_client = OpenAI(api_key=api_key)
        
        self.system_prompt = """You are a medical assistant helping healthcare workers in Uganda.
        Use the provided context from the Uganda Clinical Guidelines 2023 to answer questions.
        Always cite relevant sections of the guidelines when possible.
        Consider the following in your responses:
        1. Resource constraints and local medical practices in Uganda
        2. Clear step-by-step instructions when applicable
        3. Alternative options when certain resources might not be available
        4. Proper referral criteria when needed
        5. Emergency vs. non-emergency differentiation
        
        If you're unsure about any aspect:
        1. Acknowledge the limitations of your knowledge
        2. Suggest seeking additional medical advice
        3. Refer to specific sections of the guidelines for verification
        
        Format your responses with:
        - Clear headings when appropriate
        - Numbered steps for procedures
        - Explicit guideline citations
        - Resource-level considerations
        - Follow-up recommendations"""
    
    def query(
        self,
        question: str,
        context: Optional[str] = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """Query LLM with context"""
        try:
            if self.model_type == "lmstudio":
                return self._query_lmstudio(question, context, temperature)
            else:
                return self._query_openai(question, context, temperature)
        except Exception as e:
            logger.error(f"Query failed: {str(e)}")
            raise
    
    def _query_lmstudio(
        self,
        question: str,
        context: Optional[str],
        temperature: float
    ) -> Dict[str, Any]:
        """Query LM Studio"""
        messages = self._prepare_messages(question, context)
        
        response = requests.post(
            f"{self.base_url}/v1/chat/completions",
            json={
                "messages": messages,
                "temperature": temperature,
                "max_tokens": 2000,
                "stream": False
            }
        )
        response.raise_for_status()
        
        result = response.json()
        return {
            "response": result["choices"][0]["message"]["content"],
            "metadata": {
                "model": self.model_name,
                "type": "lmstudio",
                "timestamp": time.time()
            }
        }
    
    def _query_openai(
        self,
        question: str,
        context: Optional[str],
        temperature: float
    ) -> Dict[str, Any]:
        """Query OpenAI using new API format"""
        messages = self._prepare_messages(question, context)
        
        # Updated OpenAI API call
        response = self.openai_client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=2000
        )
        
        # Log token usage for debugging or information
        token_usage = response.usage
        logger.info(f"Token Usage: Prompt Tokens: {token_usage.prompt_tokens}, Completion Tokens: {token_usage.completion_tokens}, Total Tokens: {token_usage.total_tokens}")
        
        return {
            "response": response.choices[0].message.content,
            "metadata": {
                "model": self.model_name,
                "type": "openai",
                "timestamp": time.time(),
                "usage": {
                    "prompt_tokens": token_usage.prompt_tokens,
                    "completion_tokens": token_usage.completion_tokens,
                    "total_tokens": token_usage.total_tokens
                }
            }
        }
    
    def _prepare_messages(self, question: str, context: Optional[str]) -> List[Dict]:
        """Prepare messages for LLM"""
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        if context:
            # Format context with guidelines reference
            context_message = f"""Relevant information from Uganda Clinical Guidelines:

{context}

Please use this context to inform your response."""
            
            messages.append({
                "role": "system",
                "content": context_message
            })
        
        messages.append({"role": "user", "content": question})
        return messages
    
    def test_connection(self) -> bool:
        """Test LLM connection"""
        try:
            if self.model_type == "lmstudio":
                response = requests.get(f"{self.base_url}/v1/models")
                response.raise_for_status()
            else:
                # Test OpenAI connection using new API
                models = self.openai_client.models.list()
                if not any(model.id == self.model_name for model in models.data):
                    logger.warning(f"Model {self.model_name} not found in available models")
            
            logger.info(f"Successfully connected to {self.model_type}")
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False

# Usage example
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    # Test OpenAI client
    openai_client = LLMClient(
        model_type="openai",
        model_name="gpt-4",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    try:
        # Test connection
        if openai_client.test_connection():
            # Test query
            response = openai_client.query(
                "What are the symptoms of malaria?",
                temperature=0.3
            )
            print("Response:", response["response"])
            print("Metadata:", response["metadata"])
            # Ensure token usage is printed to console
            logger.info(f"Token Usage: {response['metadata']['usage']}")
    except Exception as e:
        print(f"Error: {e}")
