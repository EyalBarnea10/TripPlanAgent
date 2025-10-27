# TripPlanAgent - Intelligent Travel Research MCP Server

An advanced Model Context Protocol (MCP) server for comprehensive travel research, powered by AI and multiple search APIs.

## 📋 Overview

TripPlanAgent is an intelligent travel research system that provides comprehensive travel information through a unified MCP interface. It leverages AI-powered query optimization and multiple data sources to deliver actionable travel insights for destinations, accommodations, restaurants, and attractions.

## ✨ Key Features

### 🔍 Multi-Source Research
- **Web Search**: Travel guides, blogs, and expert recommendations via Google Serper API
- **Places Search**: Hotels, restaurants, attractions with ratings and reviews
- **Browser Automation**: Real-time pricing and detailed information extraction using Hyperbrowser

### 🧠 AI-Powered Intelligence
- **Query Optimization**: Automatically refines user queries for better search results using OpenAI
- **Intelligent Search Selection**: AI decides which search tools to use based on query context
- **Comprehensive Analysis**: Combines multiple data sources for complete travel insights

### ⚡ Fast & Efficient
- Parallel search execution where possible
- Optimized for quick response times
- Error-resilient with graceful fallbacks

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
OPENAI_API_KEY=your_openai_api_key_here
SERPER_API_KEY=your_serper_api_key_here
```

4. **Run the MCP server**
```bash
python servers/research_server_mcp.py
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

### As an MCP Server

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
    }
  }
}
```

### Example Queries

```python
# Through MCP client:
research_agent("Best budget hotels in Paris near Eiffel Tower")
research_agent("summer travel destinations for solo travelers")
research_agent("family-friendly restaurants in Tokyo")
research_agent("adventure activities in Switzerland")
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
│   └── research_server_mcp.py      # Main MCP server
├── agents/
│   └── research/
│       ├── research_agent.py       # Research agent implementation
│       └── agent_ruls.txt          # Agent behavior rules
├── client.py                        # MCP client (optional)
├── test_research_agent.py          # Test suite
├── requirements.txt                # Python dependencies
├── qa_expert_rules.txt             # QA guidelines
└── README.md                       # This file
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

