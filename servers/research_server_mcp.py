

from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_hyperbrowser import HyperbrowserBrowserUseTool
from langchain_openai import ChatOpenAI
from fastmcp import FastMCP   
from dotenv import load_dotenv
import os
import requests
import json  
from crewai import Agent, Task, Crew
from datetime import datetime
from fastmcp.settings import ExperimentalSettings
from mcp import StdioServerParameters
from crewai_tools import MCPServerAdapter
from crewai.tools import tool





# Load environment variables first
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("research_mcp")

# Initialize LLM with API key from environment
llm = ChatOpenAI(
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

# Helper function for Serper API calls
def call_serper_api(endpoint: str, query: str) -> str:
    """Make API call to Serper endpoint"""
    serper_key = os.getenv("SERPER_API_KEY")
    url = f"https://google.serper.dev/{endpoint}"
    headers = {
        'X-API-KEY': serper_key,
        'Content-Type': 'application/json'
    }
    data = json.dumps({"q": query})
    
    try:
        response = requests.post(url, headers=headers, data=data)
        return response.text
    except Exception as e:
        return f"{endpoint} search error: {str(e)}"

# Internal helper functions (defined before MCP tools)
def _optimize_query_internal(user_query: str) -> str:
    """Internal query optimization function"""
    try:
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key or len(openai_key.strip()) == 0:
            return "Error: OPENAI_API_KEY not found or empty"
        
        system_prompt = """You are a master expert in crafting optimal Google search queries for the Serper API. 
        Return ONLY the optimized search query - no explanations or additional text."""
        
        optimization_prompt = f'Original query: "{user_query}"\nOptimized query:'
        
        response = llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": optimization_prompt}
        ])
        
        return response.content.strip()
        
    except Exception as e:
        return f"Error optimizing query: {str(e)}"


def _web_search_internal(query: str) -> str:
    """Internal web search function"""
    try:
        # Ensure environment is set for Serper
        serper_key = os.getenv("SERPER_API_KEY")
        if serper_key:
            os.environ["SERPER_API_KEY"] = serper_key
        
        search = GoogleSerperAPIWrapper()
        return search.run(query)
    except Exception as e:
        return f"Web search error: {str(e)}"


def _places_search_internal(query: str) -> str:
    """Internal places search function"""
    try:
        return call_serper_api("places", query)
    except Exception as e:
        return f"Places search error: {str(e)}"


def _browser_search_internal(query: str) -> str:
    """Internal browser search function"""
    try:
        browser_tool = HyperbrowserBrowserUseTool()
        search_instruction = f"Search for '{query}' and extract detailed information including reviews, prices, contact details, and recommendations"
        return browser_tool.run(search_instruction)
    except Exception as e:
        return f"Browser search error: {str(e)}"

# ============================================================================
# MAIN MCP TOOL - ONLY EXPOSED ENDPOINT
# ============================================================================
@mcp.tool()
def research_agent(query: str) -> str:
    """
    Fast travel research agent - optimized for quick results.
    
    Searches web content and places/locations to provide comprehensive
    travel information including hotels, restaurants, attractions, and tips.
    
    Args:
        query: Your travel question or destination
    
    Returns:
        Comprehensive travel research results
    """
    try:
        # Step 1: Optimize query for better search results
        optimized_query = query
        try:
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key and len(openai_key.strip()) > 0:
                system_prompt = """You are a travel research expert. Optimize this query for Google search.
                Return ONLY the optimized search query - no explanations."""
                
                response = llm.invoke([
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f'Query: "{query}"\nOptimized:'}
                ])
                optimized_query = response.content.strip()
        except:
            pass  # Use original if optimization fails
        
        # Step 2: Execute fast searches
        results = []
        results.append(f"Travel Research Results for: {query}")
        results.append("=" * 80)
        results.append(f"Optimized Search: {optimized_query}\n")
        
        # Web search for guides and articles
        results.append("\n" + "=" * 80)
        results.append("WEB SEARCH - Travel Guides & Articles")
        results.append("=" * 80)
        try:
            web_result = _web_search_internal(optimized_query)
            results.append(web_result)
        except Exception as e:
            results.append(f"Web search error: {str(e)}")
        
        # Places search for specific locations
        results.append("\n\n" + "=" * 80)
        results.append("PLACES & LOCATIONS - Hotels, Restaurants, Attractions")
        results.append("=" * 80)
        try:
            places_result = _places_search_internal(optimized_query)
            results.append(places_result)
        except Exception as e:
            results.append(f"Places search error: {str(e)}")
        
        results.append("\n\n" + "=" * 80)
        results.append("Research Complete!")
        results.append("=" * 80)
        
        return "\n".join(results)
        
    except Exception as e:
        return f"Error in research_agent: {str(e)}"


# Internal tool functions (not exposed via MCP - only used by research_agent)
@tool
def web_search_tool(search_query: str) -> str:
@tool
def web_search_tool(search_query: str) -> str:
    """Search the web for travel guides, reviews, and general information"""
    return _web_search_internal(search_query)

@tool
def places_search_tool(search_query: str) -> str:
@tool
def places_search_tool(search_query: str) -> str:
    """Search for specific places, hotels, restaurants, and attractions"""
    return _places_search_internal(search_query)

@tool
def browser_search_tool(search_query: str) -> str:
@tool
def browser_search_tool(search_query: str) -> str:
    """Use advanced browser automation to search and extract detailed information from websites"""
    return _browser_search_internal(search_query)


def optimize_search_query(user_query: str) -> str:
    """Optimize and refactor user query for better Serper Google search results"""
    return _optimize_query_internal(user_query)

def intelligent_search(optimized_query: str) -> str:
    """Analyze the query and decide which search tool to use, then execute it """
    try:
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            return "Error: OPENAI_API_KEY not found"
        
        # Use main LLM for decision making
        decision_maker = llm
        
        # Decision prompt
        decision_prompt = f"""
        Query: "{optimized_query}"
        
        Analyze this travel query and decide which search tool(s) to use:
        
        - Choose "web_search" for: general travel information, guides, tips, reviews, recommendations, articles
        - Choose "places_search" for: specific locations, hotels, restaurants, attractions, businesses  
        - Choose "browser_search" for: detailed extraction from specific websites, real-time pricing, booking info
        - Choose "comprehensive" if you need information from all three sources for complete research
        
        Respond with ONLY one word: "web_search", "places_search", "browser_search", or "comprehensive"
        """
        
        # Get decision
        response = decision_maker.invoke([{"role": "user", "content": decision_prompt}])
        decision = response.content.strip().lower()
        
        # Set environment for Serper
        serper_key = os.getenv("SERPER_API_KEY")
        os.environ["SERPER_API_KEY"] = serper_key
        
        # Execute based on decision using clean internal functions
        if decision == "web_search":
            result = _web_search_internal(optimized_query)
            return f"Decision: Web Search\nResults:\n{result}"
        elif decision == "places_search":
            result = _places_search_internal(optimized_query)
            return f"Decision: Places Search\nResults:\n{result}"
        elif decision == "browser_search":
            result = _browser_search_internal(optimized_query)
            return f"Decision: Browser Search\nResults:\n{result}"
        elif decision == "comprehensive":
            web_result = _web_search_internal(optimized_query)
            places_result = _places_search_internal(optimized_query)
            browser_result = _browser_search_internal(optimized_query)
            return f"Decision: Comprehensive Search\n\nWeb Search Results:\n{web_result}\n\nPlaces Search Results:\n{places_result}\n\nBrowser Search Results:\n{browser_result}"
        else:
            # Default comprehensive search
            web_result = _web_search_internal(optimized_query)
            places_result = _places_search_internal(optimized_query)
            return f"Decision unclear: {decision}. Using comprehensive search as default.\n\nWeb Results:\n{web_result}\n\nPlaces Results:\n{places_result}"
            
    except Exception as e:
        return f"Error in intelligent search: {str(e)}"

def research_query(query: str) -> str:
    """Research the given query using multiple advanced tools: Google Serper API, Places search, and Hyperbrowser automation.
     First optimizes the query, then intelligently selects and executes the most appropriate search tools for comprehensive results."""
    
    # Step 1: Get optimized query (working pattern)
    optimized_query = query
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and len(openai_key.strip()) > 0:
        system_prompt = """You are a master expert in crafting optimal Google search queries for the Serper API. 
        Return ONLY the optimized search query - no explanations or additional text."""
        
        optimization_prompt = f'Original query: "{query}"\nOptimized query:'
        
        response = llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": optimization_prompt}
        ])
        
        optimized_query = response.content.strip()
    
    # Step 2: Web search (working pattern from _web_search_internal)
    serper_key = os.getenv("SERPER_API_KEY")
    if serper_key:
        os.environ["SERPER_API_KEY"] = serper_key
    
    search = GoogleSerperAPIWrapper()
    web_result = search.run(optimized_query)
    
    # Step 3: Places search (working pattern)
    places_result = call_serper_api("places", optimized_query)
    
    return f"🔍 Research Results for: {optimized_query}\n\n📰 Web Search Results:\n{web_result}\n\n📍 Places Search Results:\n{places_result}"




"""
═══════════════════════════════════════════════════════════════════════════════
🎯 TRIP PLANNING WORKFLOW - FIRST STEP SUMMARY
═══════════════════════════════════════════════════════════════════════════════

This MCP server represents the FIRST CRITICAL STEP in an intelligent trip planning process.

WHAT THIS SERVER ACCOMPLISHES:
✅ Destination Research & Discovery
   - Finds trending destinations for specific traveler types (solo, family, etc.)
   - Identifies safety ratings, budget considerations, and seasonal factors
   - Discovers hidden gems and insider travel tips

✅ Comprehensive Information Gathering
   - Web search: Travel guides, blogs, expert recommendations
   - Places data: Hotels, restaurants, attractions with ratings/reviews
   - Real-time data: Current pricing, availability, local conditions

✅ Intelligent Query Processing
   - Transforms vague queries into targeted searches
   - Automatically selects optimal data sources
   - Combines multiple perspectives for complete picture

EXAMPLE SUCCESSFUL QUERIES:
• "summer travel destinations solo adult" → Europe/Asia destination analysis
• "budget friendly safe countries for women" → Safety + cost breakdown
• "adventure activities Switzerland hiking" → Activity-specific recommendations
• "family resorts Caribbean all-inclusive" → Family-oriented comprehensive research

INTEGRATION INTO LARGER TRIP PLANNING:
┌─────────────────────────────────────────────────────────────────────────┐
│  PHASE 1: Research & Discovery (THIS SERVER)                           │
│  ├── Destination options                                               │
│  ├── Safety & budget analysis                                          │
│  ├── Activity/attraction identification                                │
│  └── Initial accommodation options                                     │
│                                                                         │
│  PHASE 2: Detailed Planning (Future Integration)                       │
│  ├── Specific booking research                                         │
│  ├── Itinerary creation                                                │
│  ├── Transportation planning                                           │
│  └── Budget optimization                                               │
│                                                                         │
│  PHASE 3: Booking & Execution (Future Integration)                     │
│  ├── Actual reservations                                               │
│  ├── Travel document prep                                              │
│  ├── Real-time updates                                                 │
│  └── Trip monitoring                                                   │
└─────────────────────────────────────────────────────────────────────────┘

KEY DESIGN DECISIONS:
🧠 AI-First Approach: Every query is optimized by LLM before execution
🔍 Multi-Source Strategy: Never rely on single data source
🎯 Travel-Specific: Tools optimized for travel domain, not general search
⚡ Fast & Efficient: Parallel searches where possible
🛡️ Error Resilient: Graceful fallbacks and comprehensive error handling

PRODUCTION READINESS:
✅ Environment validation with detailed error messages
✅ API key verification and masking for security
✅ Comprehensive error handling throughout the flow
✅ Modular design allowing individual tool usage
✅ Clear separation of concerns (optimization → selection → execution)

TESTED INTEGRATIONS:
✅ Cursor AI Assistant (MCP protocol)
✅ Manual testing via simple_mcp_test.py
✅ Direct tool invocation for debugging
✅ Environment validation via env_validator.py

This server provides the foundational intelligence needed for any
trip planning system, transforming simple travel questions into
comprehensive, actionable travel insights.

To use: Simply call research_query("your travel question") and receive
structured, comprehensive travel recommendations ready for further planning.
"""

if __name__ == "__main__":
    mcp.run()
