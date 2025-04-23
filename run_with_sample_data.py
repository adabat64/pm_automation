import uvicorn
import os
from app.core.mcp import MCPContext
from app.utils.sample_data import generate_sample_data
from app.utils.load_sample_data import load_sample_data

def main():
    # Generate sample data if it doesn't exist
    if not os.path.exists("sample_data"):
        print("Generating sample data...")
        generate_sample_data()
    
    # Initialize MCP context
    mcp = MCPContext("Sample Project")
    
    # Load sample data
    print("Loading sample data...")
    load_sample_data(mcp)
    
    # Run the application
    print("Starting the application...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main() 