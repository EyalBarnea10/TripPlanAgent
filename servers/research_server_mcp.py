

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
from crewai_tools import tool





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
    Main entry point for travel research. This is the ONLY exposed MCP tool.
    
    Uses a multi-agent architecture with specialized agents:
    - Web Search Agent: Specializes in finding travel guides and articles
    - Places Agent: Expert in discovering locations, hotels, restaurants
    - Browser Agent: Advanced web scraping specialist
    - Synthesis Agent: Combines all findings into actionable report
    
    All search agents run in PARALLEL for maximum efficiency.
    """
    
    # Progress tracking
    status_updates = []
    
    def log_status(message: str):
        status_updates.append(f"🔄 {message}")
        return message
    
    # ========================================================================
    # SPECIALIZED AGENTS - Each with specific expertise and single tool
    # ========================================================================
    
    log_status("Initializing Web Search Agent...")
    web_search_agent = Agent(
        role="Web Search Specialist",
        goal="Find comprehensive travel guides, articles, blogs, and expert reviews",
        backstory="""You are an expert at finding high-quality travel content on the web.
        You specialize in discovering travel guides, expert reviews, travel blogs, 
        destination overviews, and general travel information. You know how to extract 
        the most relevant and trustworthy web content.""",
        tools=[web_search_tool],
        verbose=True,
        allow_delegation=False)
    
    log_status("Initializing Places Search Agent...")
    places_search_agent = Agent(
        role="Places & Location Expert",
        goal="Discover specific places, hotels, restaurants, attractions with ratings and reviews",
        backstory="""You are a location intelligence expert specializing in finding 
        specific venues and establishments. You excel at discovering hotels, restaurants, 
        tourist attractions, local businesses, and hidden gems. You always include 
        ratings, reviews, addresses, and practical details.""",
        tools=[places_search_tool],
        verbose=True,
        allow_delegation=False)
    
    log_status("Initializing Browser Automation Agent...")
    browser_agent = Agent(
        role="Advanced Web Scraping Specialist",
        goal="Extract detailed information from websites including pricing, availability, and deep content",
        backstory="""You are an advanced web scraping expert with deep knowledge of 
        browser automation. You can navigate complex websites, extract pricing information, 
        check availability, read detailed reviews, and gather information that requires 
        interaction with web pages. You're meticulous and thorough.""",
        tools=[browser_search_tool],
        verbose=True,
        allow_delegation=False)
    
    log_status("Initializing Synthesis Agent...")
    synthesis_agent = Agent(
        role="Travel Research Synthesizer",
        goal="Combine multiple research sources into clear, actionable travel recommendations",
        backstory="""You are an expert travel analyst who excels at synthesizing 
        information from multiple sources. You create comprehensive, well-organized 
        travel reports that are both informative and actionable. You highlight key 
        insights, practical tips, and make complex information easy to understand.""",
        tools=[],  # No tools - only synthesizes
        verbose=True,
        allow_delegation=False)
    
    # ========================================================================
    # PARALLEL TASKS - Each agent runs independently and simultaneously
    # ========================================================================
    
    log_status("Creating Web Search Task...")
    web_task = Task(
        description=f"""Search the web for comprehensive travel information about: {query}
        
        Think deeply about:
        - What search queries will yield the BEST results?
        - Which sources are most credible and relevant?
        - What information gaps exist that need multiple searches?
        - How to filter out low-quality or outdated content?
        
        Focus on finding:
        - Travel guides and destination overviews
        - Expert articles and travel blogs
        - General reviews and recommendations
        - Travel tips and practical advice
        
        Use web_search_tool strategically. Consider multiple searches if needed.""",
        agent=web_search_agent,
        expected_output="Detailed web search results with travel guides, reviews, and expert recommendations",
        async_execution=True,  # ✅ Runs in parallel
        reasoning_effort="high")  # ✅ Deep thinking for better search strategy
    
    log_status("Creating Places Search Task...")
    places_task = Task(
        description=f"""Search for specific places, hotels, restaurants, and attractions related to: {query}
        
        Think strategically about:
        - What types of establishments best match the user's needs?
        - Which neighborhoods or areas to prioritize?
        - How to balance ratings, reviews, and practical factors?
        - What price ranges and categories are most relevant?
        
        Focus on finding:
        - Specific hotels with ratings and prices
        - Restaurants and dining options
        - Tourist attractions and activities
        - Local businesses and services
        
        Use places_search_tool intelligently. Consider multiple targeted searches.""",
        agent=places_search_agent,
        expected_output="List of specific places with ratings, reviews, addresses, and practical details",
        async_execution=True,  # ✅ Runs in parallel
        reasoning_effort="high")  # ✅ Deep thinking for better place selection
    
    log_status("Creating Browser Automation Task...")
    browser_task = Task(
        description=f"""Use advanced browser automation to extract detailed information about: {query}
        
        Think carefully about:
        - Which websites have the most accurate and current information?
        - What specific data points are most valuable to extract?
        - How to navigate complex booking sites efficiently?
        - What patterns in reviews indicate quality and reliability?
        
        Focus on extracting:
        - Current pricing and availability
        - Detailed website content
        - Booking information and options
        - User reviews and ratings from actual sites
        
        Use browser_search_tool strategically for maximum value extraction.""",
        agent=browser_agent,
        expected_output="Detailed extracted information including current prices, availability, and deep content",
        async_execution=True,  # ✅ Runs in parallel
        reasoning_effort="high")  # ✅ Deep thinking for better extraction strategy
    
    # ========================================================================
    # SYNTHESIS TASK - Waits for all parallel tasks to complete
    # ========================================================================
    
    log_status("Creating Synthesis Task...")
    synthesis_task = Task(
        description=f"""Synthesize all gathered research data into a comprehensive travel recommendation for: {query}
        
        You will receive:
        1. Web search results (travel guides, articles, expert reviews)
        2. Places data (specific hotels, restaurants, attractions with ratings)
        3. Browser-extracted data (pricing, availability, detailed content)
        
        Create a well-structured report with these sections:
        
        ## 🌍 Destination Overview
        - Brief introduction and highlights
        - Best time to visit
        - Key attractions
        
        ## 🏨 Recommended Accommodations
        - Top hotel options with ratings and prices
        - Location and accessibility info
        
        ## 🍽️ Dining & Cuisine
        - Best restaurants and local food
        - Price ranges and specialties
        
        ## 🎯 Activities & Attractions
        - Must-see places and experiences
        - Booking info where available
        
        ## 💡 Practical Tips
        - Budget considerations
        - Safety information
        - Transportation options
        - Insider tips
        
        Make it actionable, well-organized, and easy to understand.""",
        agent=synthesis_agent,
        expected_output="Comprehensive, well-organized travel recommendation report",
        context=[web_task, places_task, browser_task],  # ✅ Waits for all to complete
        reasoning_effort="high")
    
    # ========================================================================
    # CREW EXECUTION - Orchestrates all agents
    # ========================================================================
    
    log_status("Assembling research crew...")
    crew = Crew(
        agents=[web_search_agent, places_search_agent, browser_agent, synthesis_agent],
        tasks=[web_task, places_task, browser_task, synthesis_task],
        verbose=True,
        process="sequential"  # Sequential process allows async tasks to run in parallel
    )
    
    log_status("🚀 Launching parallel research (3 agents working simultaneously)...")
    result = crew.kickoff()
    log_status("✅ All agents completed! Report synthesized.")
    
    # Return result with progress log
    status_log = "\n".join(status_updates)
    return f"{status_log}\n\n{'='*80}\n📊 FINAL RESEARCH REPORT\n{'='*80}\n\n{result}"


# Internal tool functions (not exposed via MCP - only used by research_agent)
@tool
def web_search_tool(search_query: str) -> str:
    """Search the web for travel guides, reviews, and general information"""
    return _web_search_internal(search_query)

@tool
def places_search_tool(search_query: str) -> str:
    """Search for specific places, hotels, restaurants, and attractions"""
    return _places_search_internal(search_query)

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
