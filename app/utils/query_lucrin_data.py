from app.core.mcp import MCPContext
from app.utils.llm_service import LLMService

def analyze_project_data(mcp: MCPContext):
    """Analyze project data using LLM."""
    llm_service = LLMService()
    
    # Example queries about project data
    queries = [
        "What's the total hours spent on Design workstream?",
        "Show me the distribution of hours across workstreams",
        "What's the approval status breakdown?",
        "Which workstream has the most pending hours?"
    ]
    
    print("\n=== Project Data Analysis ===\n")
    
    for query in queries:
        response = llm_service.query(query, mcp)
        print(f"\nQuery: {query}")
        print(f"Response: {response}\n")
        print("-" * 80)

if __name__ == "__main__":
    from app.core.mcp import get_mcp
    mcp = get_mcp()
    analyze_project_data(mcp) 