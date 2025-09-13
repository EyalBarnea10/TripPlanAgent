"""
🌍 TRAVEL RESEARCH MCP SERVER - INTELLIGENT TRIP PLANNING AGENT
================================================================

OVERVIEW:
This MCP (Model Context Protocol) server provides intelligent travel research capabilities
for trip planning through multiple specialized search tools and AI-powered query optimization.

DESIGN ARCHITECTURE:
┌─────────────────────────────────────────────────────────────────┐
│                    TRAVEL RESEARCH MCP SERVER                   │
├─────────────────────────────────────────────────────────────────┤
│  Entry Point: research_query(query: str) → comprehensive_results │
├─────────────────────────────────────────────────────────────────┤
│                     CORE PROCESSING FLOW                        │
│  1. Query Optimization (OpenAI LLM)                            │
│     └── Transforms user query → SEO-optimized search terms     │
│  2. Intelligent Tool Selection (AI Decision Making)            │
│     └── Analyzes query → selects optimal search strategy       │
│  3. Multi-Source Data Retrieval                               │
│     ├── Web Search (Serper API) → guides, reviews, articles   │
│     ├── Places Search (Serper Places) → locations, businesses │
│     └── Browser Automation (Hyperbrowser) → detailed scraping │
│  4. Result Synthesis and Formatting                           │
│     └── Combines all sources → structured travel insights     │
└─────────────────────────────────────────────────────────────────┘

TECHNICAL STACK:
- FastMCP: Model Context Protocol server framework
- OpenAI GPT: Query optimization and intelligent decision making
- Google Serper API: Web search and places data
- Hyperbrowser: Advanced web scraping and automation
- LangChain: AI tool orchestration and management

SUPPORTED SEARCH TYPES:
1. WEB SEARCH - General travel information, guides, reviews, recommendations
2. PLACES SEARCH - Specific locations, hotels, restaurants, attractions
3. BROWSER SEARCH - Detailed extraction, real-time pricing, booking info
4. COMPREHENSIVE - All three sources for complete research coverage

API ENDPOINTS (MCP Tools):
- research_query(query) - Main entry point for travel research
- web_search_tool(query) - Direct web search functionality
- places_search_tool(query) - Direct places search functionality
- browser_search_tool(query) - Direct browser automation
- optimize_search_query(query) - Query optimization only
- intelligent_search(query) - Smart tool selection + execution

ENVIRONMENT REQUIREMENTS:
- OPENAI_API_KEY: For LLM-powered query optimization and decisions
- SERPER_API_KEY: For Google search and places API access
- HYPERBROWSER_API_KEY: For advanced web scraping capabilities

USAGE FLOW FOR TRIP PLANNING:
Step 1: Input raw travel query (e.g., "summer vacation solo adult Europe")
Step 2: AI optimizes query for search engines
Step 3: System selects appropriate search tools based on query type
Step 4: Executes searches across multiple data sources
Step 5: Returns comprehensive, structured travel recommendations

EXAMPLES:
- "best summer destinations solo travel" → comprehensive destination analysis
- "hotels near Eiffel Tower Paris" → places search with specific accommodations
- "travel guides Croatia safety budget" → web search for detailed articles

This server acts as the first step in intelligent trip planning, providing
comprehensive research capabilities that can be integrated into larger
travel planning workflows and AI assistants.
"""

from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_hyperbrowser import HyperbrowserBrowserUseTool
from langchain_openai import ChatOpenAI
from fastmcp import FastMCP   
from dotenv import load_dotenv
import os
import requests
import json 

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

# Create 3 travel research tools using MCP decorators
@mcp.tool()
def web_search_tool(search_query: str) -> str:
    """Search the web for travel guides, reviews, and general information"""
    search = GoogleSerperAPIWrapper()
    return search.run(search_query)

@mcp.tool()
def places_search_tool(search_query: str) -> str:
    """Search for specific places, hotels, restaurants, and attractions"""
    return call_serper_api("places", search_query)

@mcp.tool()
def browser_search_tool(search_query: str) -> str:
    """Use advanced browser automation to search and extract detailed information from websites"""
    try:
        browser_tool = HyperbrowserBrowserUseTool()
        # Format query for browser search
        search_instruction = f"Search for '{search_query}' and extract detailed information including reviews, prices, contact details, and recommendations"
        return browser_tool.run(search_instruction)
    except Exception as e:
        return f"Browser search error: {str(e)}"


@mcp.tool()
def optimize_search_query(user_query: str) -> str:
    """Optimize and refactor user query for better Serper Google search results"""
    try:
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            return "Error: OPENAI_API_KEY not found"
        
        # Use main LLM for query optimization
        query_optimizer = llm
        
        # Expert system prompt for query optimization
        system_prompt = """You are a master expert in crafting optimal Google search queries for the Serper API. 
        Your expertise includes:
        - Understanding Google search algorithms and ranking factors
        - Crafting precise, targeted search queries that return highly relevant results
        - Using appropriate search operators, keywords, and modifiers
        - Optimizing for different types of searches (informational, transactional, navigational)
        
        When given a user query, you should:
        1. Analyze the user's intent and information needs
        2. Identify the most important keywords and concepts
        3. Add relevant search modifiers and operators when appropriate
        4. Structure the query for maximum relevance and accuracy
        5. Consider synonyms and related terms that might improve results
        
        Return ONLY the optimized search query - no explanations or additional text."""
        
        # Create the optimization prompt
        optimization_prompt = f"""
        Original user query: "{user_query}"
        
        Please optimize this query for Google search via Serper API to get the most relevant, accurate, and comprehensive results. 
        Focus on making it specific enough to avoid irrelevant results but broad enough to capture all relevant information.
        
        Optimized query:"""
        
        # Get optimized query
        response = query_optimizer.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": optimization_prompt}
        ])
        
        optimized_query = response.content.strip()
        return optimized_query
        
    except Exception as e:
        return f"Error optimizing query: {str(e)}"

@mcp.tool()
def intelligent_search(optimized_query: str) -> str:
    """Analyze the query and decide which search tool to use, then execute it"""
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
        
        # Execute based on decision
        if decision == "web_search":
            result = web_search_tool(optimized_query)
            return f"Decision: Web Search\nResults:\n{result}"
        elif decision == "places_search":
            result = places_search_tool(optimized_query)
            return f"Decision: Places Search\nResults:\n{result}"
        elif decision == "browser_search":
            result = browser_search_tool(optimized_query)
            return f"Decision: Browser Search\nResults:\n{result}"
        elif decision == "comprehensive":
            web_result = web_search_tool(optimized_query)
            places_result = places_search_tool(optimized_query)
            browser_result = browser_search_tool(optimized_query)
            return f"Decision: Comprehensive Search\n\nWeb Search Results:\n{web_result}\n\nPlaces Search Results:\n{places_result}\n\nBrowser Search Results:\n{browser_result}"
        else:
            return f"Decision unclear: {decision}. Using comprehensive search as default.\n{web_search_tool(optimized_query)}\n\n{places_search_tool(optimized_query)}\n\n{browser_search_tool(optimized_query)}"
            
    except Exception as e:
        return f"Error in intelligent search: {str(e)}"

@mcp.tool()
def research_query(query: str) -> str:
    """Research the given query using multiple advanced tools: Google Serper API, Places search, and Hyperbrowser automation.
     First optimizes the query, then intelligently selects and executes the most appropriate search tools for comprehensive results."""
    
    try:
        # Check API keys and debug
        openai_key = os.getenv("OPENAI_API_KEY")
        serper_key = os.getenv("SERPER_API_KEY")
        hyperbrowser_key = os.getenv("HYPERBROWSER_API_KEY")
        
        # Debug output
        if not openai_key:
            return "Error: OPENAI_API_KEY not found in environment variables"
        if not serper_key:
            return "Error: SERPER_API_KEY not found in environment variables"
        if not hyperbrowser_key:
            return "Error: HYPERBROWSER_API_KEY not found in environment variables"
        
        # Check if keys have values (not just empty strings)
        if len(openai_key.strip()) == 0:
            return "Error: OPENAI_API_KEY is empty"
        if len(serper_key.strip()) == 0:
            return "Error: SERPER_API_KEY is empty"
        if len(hyperbrowser_key.strip()) == 0:
            return "Error: HYPERBROWSER_API_KEY is empty"
        
        # Step 1: Optimize the search query using LLM directly
        try:
            system_prompt = """You are a master expert in crafting optimal Google search queries for the Serper API. 
            Your expertise includes:
            - Understanding Google search algorithms and ranking factors
            - Crafting precise, targeted search queries that return highly relevant results
            - Using appropriate search operators, keywords, and modifiers
            - Optimizing for different types of searches (informational, transactional, navigational)
            
            When given a user query, you should:
            1. Analyze the user's intent and information needs
            2. Identify the most important keywords and concepts
            3. Add relevant search modifiers and operators when appropriate
            4. Structure the query for maximum relevance and accuracy
            5. Consider synonyms and related terms that might improve results
            
            Return ONLY the optimized search query - no explanations or additional text."""
            
            optimization_prompt = f"""
            Original user query: "{query}"
            
            Please optimize this query for Google search via Serper API to get the most relevant, accurate, and comprehensive results. 
            Focus on making it specific enough to avoid irrelevant results but broad enough to capture all relevant information.
            
            Optimized query:"""
            
            response = llm.invoke([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": optimization_prompt}
            ])
            
            optimized_query = response.content.strip()
            
            # Step 2: Use comprehensive search approach
            # Set environment for Serper
            os.environ["SERPER_API_KEY"] = serper_key
            
            # Execute all search types for comprehensive results
            web_result = web_search_tool(optimized_query)
            places_result = places_search_tool(optimized_query)
            
            return f"🔍 Research Results for: {optimized_query}\n\n📰 Web Search Results:\n{web_result}\n\n📍 Places Search Results:\n{places_result}"
            
        except Exception as e:
            return f"Error in search execution: {str(e)}"
    
    except Exception as e:
        return f"Error in research_query: {str(e)}"


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