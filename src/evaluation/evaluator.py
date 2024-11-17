from transformers import AutoTokenizer, AutoModelForCausalLM
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class MediTronEvaluator:
    def __init__(self, model_name="epfl-llm/meditron-7b"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype="auto")

    def evaluate_response(self, query: str, response: str, reference: str):
        """
        Evaluate a response using MediTron for medical accuracy, relevance, and completeness.
        """
        accuracy = self._calculate_accuracy(response, reference)
        relevance = self._calculate_relevance(query, response)
        return {
            "accuracy": accuracy,
            "relevance": relevance,
        }

    def _calculate_accuracy(self, response: str, reference: str) -> float:
        """
        Calculate overlap-based accuracy of response against reference.
        """
        response_tokens = set(response.lower().split())
        reference_tokens = set(reference.lower().split())
        overlap = response_tokens.intersection(reference_tokens)
        return len(overlap) / len(reference_tokens)

    def _calculate_relevance(self, query: str, response: str) -> float:
        """
        Calculate relevance using cosine similarity between embeddings.
        """
        query_embedding = self._get_embedding(query)
        response_embedding = self._get_embedding(response)
        return cosine_similarity([query_embedding], [response_embedding])[0][0]

    def _get_embedding(self, text: str) -> np.ndarray:
        """
        Generate embeddings for the input text using MediTron.
        """
        inputs = self.tokenizer(text, return_tensors="pt")
        outputs = self.model(**inputs, output_hidden_states=True)
        embedding = outputs.hidden_states[-1].mean(dim=1).detach().numpy()
        return embedding.flatten()
