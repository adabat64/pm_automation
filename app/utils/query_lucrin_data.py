import os
from pathlib import Path
from dotenv import load_dotenv
from app.utils.llm_service import LLMService

def main():
    # Load environment variables from .env file
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)
    
    # Initialize the LLM service
    service = LLMService()
    
    # Example queries about Lucrin data
    queries = [
        "What's the total hours spent on UX UI & Design workstream?",
        "How many hours are pending approval (Open status)?",
        "What's the distribution of hours across different workstreams?",
        "Who has logged the most hours in the SEO Analytics & Strategy workstream?",
        "What's the trend in hours logged over the past month?"
    ]
    
    print("\n=== Lucrin Project Analysis ===\n")
    
    for query in queries:
        print(f"\nQuery: {query}")
        print("-" * 50)
        response = service.query_project_data(query)
        print(response)
        print("-" * 50)

if __name__ == "__main__":
    main() 