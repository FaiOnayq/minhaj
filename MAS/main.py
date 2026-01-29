"""
Simple Multi-Agent System
Run: python main.py
"""
from workflow import run


def main():
    print("=" * 60)
    print("MULTI-AGENT RESEARCH SYSTEM")
    print("=" * 60)
    
    # Your query
    query = "machine learning course for biginners"
    
    print(f"\nQuery: {query}\n")
    print("Running...\n")
    
    # Run workflow
    result = run(query)
    
    # Display result
    print("\n" + "=" * 60)
    print("RESULT:")
    print("=" * 60)
    print(result)
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()