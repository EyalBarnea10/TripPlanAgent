#!/usr/bin/env python3
"""
Test script for the Travel Research Agent
Run this script to verify the research agent functionality.
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.research.research_agent import TravelResearchAgent


async def test_research_agent():
    """Test the research agent with a sample query."""
    print("🔍 Initializing Travel Research Agent...")
    
    try:
        # Initialize the agent
        agent = TravelResearchAgent()
        
        # Get agent status
        status = agent.get_agent_status()
        print(f"✅ Agent Status: {status}")
        
        # Test query
        test_query = "Best budget hotels in Paris near Eiffel Tower"
        print(f"\n🎯 Testing with query: '{test_query}'")
        
        # Perform research
        result = await agent.research_query(test_query)
        
        # Display results
        print("\n" + "="*60)
        print("📊 RESEARCH RESULTS")
        print("="*60)
        print(f"Query: {result.query}")
        print(f"Confidence Score: {result.confidence:.2f}")
        print(f"Sources Found: {len(result.sources)}")
        print(f"Recommendations: {len(result.recommendations)}")
        print(f"Timestamp: {result.timestamp}")
        
        print("\n📝 Synthesis:")
        print("-" * 40)
        print(result.synthesis)
        
        if result.recommendations:
            print("\n💡 Recommendations:")
            print("-" * 40)
            for i, rec in enumerate(result.recommendations, 1):
                print(f"{i}. {rec}")
        
        if result.sources:
            print("\n🔗 Sources:")
            print("-" * 40)
            for source in result.sources:
                print(f"• {source}")
        
        print("\n✅ Research agent test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False
    
    return True


def main():
    """Main test function."""
    print("🚀 Starting Travel Research Agent Test")
    print("="*60)
    
    # Check environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please check your .env file")
        return
    
    # Run the async test
    success = asyncio.run(test_research_agent())
    
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️ Some tests failed. Please check the error messages above.")


if __name__ == "__main__":
    main()

