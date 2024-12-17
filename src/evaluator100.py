import pandas as pd
import os
from src.rag.llm_client import LLMClient
from src.logger import setup_logger
from openai import OpenAI
from src.config import settings

class RAGResponseGenerator:
    def __init__(self, input_csv_path, output_csv_path, openai_api_key):
        """
        Initialize RAG Response Generator
        
        :param input_csv_path: Path to input CSV with questions
        :param output_csv_path: Path to output CSV with responses
        :param openai_api_key: OpenAI API key for evaluation
        """
        # Setup logging
        self.logger = setup_logger("rag_response_generator")
        
        # Load input questions
        self.input_df = pd.read_csv(input_csv_path)
        self.output_csv_path = output_csv_path
        output_dir = os.path.dirname(self.output_csv_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            self.logger.info(f"Created output directory: {output_dir}")
                
        # Initialize LLM clients
        self.logger.info("Initializing LM Studio client...")
        self.lmstudio_client = LLMClient(
            model_type="lmstudio",
            model_name="llama-3.2-3b-instruct"
        )
        
        self.logger.info("Initializing OpenAI client...")
        self.openai_client = LLMClient(
            model_type="openai",
            model_name="gpt-4",
            api_key=settings.OPENAI_API_KEY
        )
        
    def generate_responses(self, num_runs=1):
        """
        Generate multiple responses for each question using both models
        
        :param num_runs: Number of response generations per question
        :return: DataFrame with responses
        """
        results = []
        
        for idx, row in self.input_df.iterrows():
            question = row['Questions']
            self.logger.info(f"Processing question: {question}")
            
            # # Generate LM Studio responses
            # lm_studio_responses = self._generate_model_responses(
            #     self.lmstudio_client, question, num_runs
            # )
            
            # Generate OpenAI responses
            openai_responses = self._generate_model_responses(
                self.openai_client, question, num_runs
            )
            
            # Prepare result row
            result_row = {
                'Questions': question,
                # **{f'response {i+1}': resp for i, resp in enumerate(lm_studio_responses)},
                **{f'response': resp for resp in enumerate(openai_responses)}
            }
            
            results.append(result_row)
        
        # Convert to DataFrame
        results_df = pd.DataFrame(results)
        
        # Save to CSV
        results_df.to_csv(self.output_csv_path, index=False)
        self.logger.info(f"Responses saved to {self.output_csv_path}")
        
        return results_df
    
    def _generate_model_responses(self, client, question, num_runs):
        """
        Generate multiple responses for a single question using a specific client
        
        :param client: LLM client (LMStudio or OpenAI)
        :param question: Question to generate responses for
        :param num_runs: Number of response generations
        :return: List of generated responses
        """
        responses = []
        
        for run in range(num_runs):
            try:
                response = client.query(question)
                responses.append(response['response'])
                self.logger.info(f"Generated response {run+1} for question")
            except Exception as e:
                self.logger.error(f"Response generation failed: {str(e)}")
                responses.append("Response generation failed")
        
        return responses

# Usage example
if __name__ == "__main__":
    # Configuration
    from src.config import settings
    INPUT_CSV_PATH = "../questionlist.csv"
    OUTPUT_CSV_PATH = "../results/100responses.csv"
    OPENAI_API_KEY = settings.OPENAI_API_KEY
    
    # Initialize and run
    generator = RAGResponseGenerator(INPUT_CSV_PATH, OUTPUT_CSV_PATH, OPENAI_API_KEY)
    results = generator.generate_responses()