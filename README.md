# TripPlanAgent - Intelligent Travel Planning & Booking MCP Servers

An advanced Model Context Protocol (MCP) system for comprehensive travel research, flight search, and booking capabilities, powered by AI and multiple travel APIs.

## 📋 Overview

TripPlanAgent is an intelligent travel planning system that provides comprehensive travel services through unified MCP interfaces. It leverages AI-powered query optimization, real-time flight data, and multiple data sources to deliver complete travel planning from destination research to flight booking.

### 🎯 Two-Phase System

1. **Phase 1: Travel Research Agent** (`research_server_mcp.py`)
   - Destination research and recommendations
   - Hotels, restaurants, and attractions discovery
   - Travel guides and expert insights

2. **Phase 2: Flight Booking Agent** (`flights_booking_mcp.py`) ✨ NEW
   - Real-time flight search across 400+ airlines
   - Airport code lookup
   - Multi-city and round-trip support
   - Powered by Amadeus API

## ✨ Key Features

### 📍 Travel Research Agent
- **🔍 Multi-Source Research**: Web search, places data, and browser automation
- **🧠 AI-Powered Intelligence**: Query optimization and intelligent search selection
- **⚡ Fast & Efficient**: Parallel execution and error-resilient design
- **🏨 Comprehensive Data**: Hotels, restaurants, attractions with ratings

### ✈️ Flight Booking Agent (NEW)
- **🛫 Real-Time Flight Search**: Live pricing from 400+ airlines worldwide
- **🌍 Global Coverage**: 190+ countries, all major airports
- **🎫 Flexible Options**: One-way, round-trip, multi-city support
- **💺 Travel Classes**: Economy, Premium, Business, First class
- **🔍 Airport Discovery**: Find IATA codes by city or airport name
- **💰 Competitive Pricing**: Powered by Amadeus GDS platform

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  User Query (via MCP Client - Cursor AI, Claude Desktop)   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  FastMCP Server (research_server_mcp.py)                    │
│  └─ research_agent() - Main MCP Tool                        │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
┌─────────────┐ ┌──────────┐ ┌──────────────┐
│ Query       │ │ Web      │ │ Places       │
│ Optimizer   │ │ Search   │ │ Search       │
│ (OpenAI)    │ │ (Serper) │ │ (Serper)     │
└─────────────┘ └──────────┘ └──────────────┘
```

## 🚀 Installation

### Prerequisites

- Python 3.8+
- OpenAI API Key
- Google Serper API Key
- Hyperbrowser API credentials (optional)

### Setup Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd TripPlanAgent
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**

Create a `.env` file in the project root:
```env
# Required for Research Agent
OPENAI_API_KEY=your_openai_api_key_here
SERPER_API_KEY=your_serper_api_key_here

# Required for Flight Booking Agent (optional)
AMADEUS_API_KEY=your_amadeus_api_key_here
AMADEUS_API_SECRET=your_amadeus_api_secret_here
```

**Get Amadeus API credentials** (for flight booking):
- Visit [https://developers.amadeus.com/](https://developers.amadeus.com/)
- Register and create a new app (free tier available)
- See [FLIGHT_BOOKING_SETUP.md](./FLIGHT_BOOKING_SETUP.md) for detailed instructions

4. **Run the MCP servers**
```bash
# Run Research Agent
python servers/research_server_mcp.py

# Run Flight Booking Agent
python servers/flights_booking_mcp.py
```

## 📦 Dependencies

- **fastmcp**: MCP server framework
- **langchain-openai**: OpenAI LLM integration
- **langchain-community**: Community tools including Google Serper
- **langchain-hyperbrowser**: Browser automation tool
- **crewai**: Multi-agent orchestration framework
- **python-dotenv**: Environment variable management
- **requests**: HTTP client library

## 🔧 Usage

### As MCP Servers

Configure in your MCP client (e.g., Cursor AI, Claude Desktop):

```json
{
  "mcpServers": {
    "research_mcp": {
      "command": "python",
      "args": ["c:/ai_for_developer/TripPlanAgent/servers/research_server_mcp.py"],
      "env": {
        "OPENAI_API_KEY": "your_key_here",
        "SERPER_API_KEY": "your_key_here"
      }
    },
    "flights_booking_mcp": {
      "command": "python",
      "args": ["c:/ai_for_developer/TripPlanAgent/servers/flights_booking_mcp.py"],
      "env": {
        "AMADEUS_API_KEY": "your_amadeus_key",
        "AMADEUS_API_SECRET": "your_amadeus_secret"
      }
    }
  }
}
```

### Example Queries

**Research Agent:**
```python
# Destination and accommodation research
research_agent("Best budget hotels in Paris near Eiffel Tower")
research_agent("summer travel destinations for solo travelers")
research_agent("family-friendly restaurants in Tokyo")
research_agent("Naples Italy March trip with teenagers")
```

**Flight Booking Agent:**
```python
# Find airport codes
find_airports("Naples")
find_airports("New York")

# Search flights
search_flights("JFK", "NAP", "2025-03-15", "2025-03-22", 2, "ECONOMY")
search_flights("LAX", "FCO", "2025-06-01", None, 1, "BUSINESS")  # One-way

# Get help
flight_booking_help()
```

## 🎯 Use Cases

### Destination Research
- Find trending destinations for specific traveler types (solo, family, couples)
- Analyze safety ratings and budget considerations
- Discover seasonal factors and best times to visit

### Accommodation Discovery
- Search hotels by location, price range, and amenities
- Get ratings, reviews, and real-time pricing
- Find hidden gems and local recommendations

### Activity Planning
- Discover attractions and activities
- Get restaurant recommendations
- Find local experiences and tours

### Trip Planning Integration
This server represents **Phase 1** of a complete trip planning workflow:

**Phase 1: Research & Discovery** (Current)
- Destination options
- Safety & budget analysis
- Activity identification
- Initial accommodation options

**Phase 2: Detailed Planning** (Future)
- Specific booking research
- Itinerary creation
- Transportation planning
- Budget optimization

**Phase 3: Booking & Execution** (Future)
- Actual reservations
- Travel document preparation
- Real-time updates
- Trip monitoring

## 🛠️ Project Structure

```
TripPlanAgent/
├── servers/
│   ├── research_server_mcp.py      # Travel Research MCP server
│   └── flights_booking_mcp.py      # Flight Booking MCP server (NEW)
├── agents/
│   └── research/
│       ├── research_agent.py       # Research agent implementation
│       └── agent_ruls.txt          # Agent behavior rules
├── test_research_agent.py          # Research agent test suite
├── test_flight_booking.py          # Flight booking test suite (NEW)
├── naples_research_simple.py       # Example: Naples trip research
├── requirements.txt                # Python dependencies
├── README.md                       # Main documentation
├── FLIGHT_BOOKING_SETUP.md         # Flight booking setup guide (NEW)
└── qa_expert_rules.txt             # QA guidelines
```

## 🔒 Security & Best Practices

- ✅ Environment variable validation with detailed error messages
- ✅ API key verification and secure storage
- ✅ Comprehensive error handling throughout
- ✅ Modular design for maintainability
- ✅ Clear separation of concerns
- ✅ Rate limiting awareness to avoid API throttling

## 🧪 Testing

Run the test suite:
```bash
python test_research_agent.py
```

The test script validates:
- Agent initialization
- Query processing
- Multi-source data retrieval
- Result synthesis

## 📊 API Integration

### Google Serper API
Used for web search and places data. Provides:
- Real-time search results
- Places/business information
- Reviews and ratings

### OpenAI API
Used for:
- Query optimization
- Intelligent search tool selection
- Result synthesis

### Hyperbrowser (Optional)
Advanced browser automation for:
- JavaScript-heavy websites
- Real-time pricing extraction
- Complex navigation flows

## 🎨 Design Principles

1. **AI-First Approach**: Every query optimized by LLM before execution
2. **Multi-Source Strategy**: Never rely on a single data source
3. **Travel-Specific**: Tools optimized for travel domain
4. **Fast & Efficient**: Parallel searches where possible
5. **Error Resilient**: Graceful fallbacks and comprehensive error handling

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional search sources
- Enhanced query optimization
- Performance optimizations
- Extended test coverage
- Integration with booking APIs

## 📝 License

This project is provided as-is for educational and research purposes.

## 🔗 Resources

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [LangChain Documentation](https://python.langchain.com/)
- [CrewAI Documentation](https://docs.crewai.com/)
- [Google Serper API](https://serper.dev/)
- [Model Context Protocol](https://modelcontextprotocol.io/)

## 📞 Support

For issues, questions, or contributions, please open an issue in the repository.

---

**Built with ❤️ using AI-powered tools and Model Context Protocol**

