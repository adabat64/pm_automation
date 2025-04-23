import os
from typing import Dict, Any, Optional
from openai import OpenAI
from pathlib import Path
import json
from datetime import datetime, timedelta
import hashlib
from app.utils.llm_interface import ProjectDataAnalyzer, format_llm_prompt

class LLMService:
    """Service for interacting with OpenAI's LLM API with caching."""
    
    def __init__(self, api_key: Optional[str] = None, cache_dir: str = "cache", cache_duration: int = 24):
        """Initialize the LLM service with OpenAI API key and caching."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it to the constructor.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.analyzer = ProjectDataAnalyzer()
        
        # Setup caching
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_duration = timedelta(hours=cache_duration)
    
    def _get_cache_path(self, query: str, model: str) -> Path:
        """Get the cache file path for a query."""
        # Create a unique hash for the query and model
        query_hash = hashlib.md5(f"{query}:{model}".encode()).hexdigest()
        return self.cache_dir / f"{query_hash}.json"
    
    def _load_from_cache(self, cache_path: Path) -> Optional[str]:
        """Load response from cache if it exists and is not expired."""
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r') as f:
                cached = json.load(f)
            
            # Check if cache is expired
            cached_time = datetime.fromisoformat(cached['timestamp'])
            if datetime.now() - cached_time > self.cache_duration:
                return None
            
            return cached['response']
        except Exception:
            return None
    
    def _save_to_cache(self, cache_path: Path, response: str):
        """Save response to cache."""
        try:
            with open(cache_path, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'response': response
                }, f)
        except Exception:
            pass  # Silently fail if caching fails
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt that sets the context for the LLM."""
        return """You are a project management assistant analyzing timesheet and budget data. 
Your role is to:
1. Analyze project data and provide clear, concise insights
2. Identify trends and patterns in timesheet entries
3. Compare actual hours against budgets
4. Highlight potential issues or areas of concern
5. Provide recommendations based on the data

When analyzing data:
- Focus on key metrics and trends
- Highlight significant deviations from budgets
- Identify potential resource allocation issues
- Suggest optimizations where appropriate
- Maintain data privacy by not revealing specific user details

Format your responses in a clear, structured way using markdown."""
    
    def query_project_data(self, query: str, model: str = "gpt-3.5-turbo") -> str:
        """Query the project data using the LLM with caching."""
        # Check cache first
        cache_path = self._get_cache_path(query, model)
        cached_response = self._load_from_cache(cache_path)
        if cached_response:
            return cached_response
        
        # Prepare the context and format the prompt
        context = self.analyzer.prepare_llm_context()
        user_prompt = format_llm_prompt(query, context)
        
        try:
            # Make the API call
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": self._create_system_prompt()},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1000,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            # Extract the response
            result = response.choices[0].message.content
            
            # Cache the response
            self._save_to_cache(cache_path, result)
            
            return result
            
        except Exception as e:
            return f"Error querying LLM: {str(e)}"
    
    def get_project_summary(self, model: str = "gpt-3.5-turbo") -> str:
        """Get a comprehensive project summary."""
        query = """Please provide a comprehensive summary of the project status, including:
1. Overall progress and key metrics
2. Budget utilization and forecasts
3. Resource allocation and workload distribution
4. Notable trends and patterns
5. Potential areas of concern or attention
6. Recommendations for optimization"""
        
        return self.query_project_data(query, model)
    
    def analyze_workstream(self, workstream: str, model: str = "gpt-3.5-turbo") -> str:
        """Analyze a specific workstream."""
        query = f"""Please analyze the following aspects of the {workstream} workstream:
1. Hours logged vs. budget
2. Resource allocation and workload
3. Progress and completion status
4. Cost analysis
5. Recommendations for optimization"""
        
        return self.query_project_data(query, model)
    
    def get_resource_analysis(self, model: str = "gpt-3.5-turbo") -> str:
        """Analyze resource allocation and utilization."""
        query = """Please analyze resource allocation and utilization, including:
1. Workload distribution across team members
2. Hours per workstream
3. Resource utilization trends
4. Potential bottlenecks or underutilization
5. Recommendations for resource optimization"""
        
        return self.query_project_data(query, model)

def main():
    """Example usage of the LLM service."""
    # Initialize the service with 24-hour cache
    service = LLMService(cache_duration=24)
    
    # Example queries (responses will be cached)
    print("\n=== Project Summary ===")
    print(service.get_project_summary())
    
    print("\n=== Workstream Analysis ===")
    print(service.analyze_workstream("Workstream_1"))
    
    print("\n=== Resource Analysis ===")
    print(service.get_resource_analysis())
    
    # Custom query example
    print("\n=== Custom Query ===")
    custom_query = "What's the trend in hours logged over the past month and how does it compare to the budget?"
    print(service.query_project_data(custom_query))

if __name__ == "__main__":
    main() 