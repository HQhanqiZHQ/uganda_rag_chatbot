import os
import pandas as pd
from datetime import datetime
from src.evaluator import RAGEvaluator
from src.config import settings

def main():
    # Load pre-computed responses from a CSV file
    responses_df = pd.read_csv('pre_computed_responses.csv')

    print("Initializing evaluator...")
    evaluator = RAGEvaluator(openai_api_key=settings.OPENAI_API_KEY)
    
    print("Starting evaluation...")
    results_df = evaluator.evaluate_responses(responses_df)
    
    # Create results directory if it doesn't exist
    if not os.path.exists('results'):
        os.makedirs('results')
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_path = f'results/rag_evaluation_{timestamp}.csv'
    results_df.to_csv(results_path, index=False)
    print(f"\nResults saved to {results_path}")
    
    # Print summary
    print("\nEvaluation Summary:")
    for idx, row in results_df.iterrows():
        print(f"\nQuestion: {row['Questions']}")
        
        print("\nLM Studio Responses:")
        for lmstudio_response, lmstudio_eval in zip(row['lmstudio_responses'], row['lmstudio_evaluations']):
            print(f"Response: {lmstudio_response}")
            print(f"Evaluation: {lmstudio_eval}")
            print("-" * 80)
        
        print("\nOpenAI Responses:")
        for openai_response, openai_eval in zip(row['openai_responses'], row['openai_evaluations']):
            print(f"Response: {openai_response}")
            print(f"Evaluation: {openai_eval}")
            print("-" * 80)
    
    return results_df

if __name__ == "__main__":
    results = main()