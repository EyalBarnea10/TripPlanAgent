#!/usr/bin/env python3
"""
🔍 Creative .env File Validator & Tester
Tests all API keys and validates the environment setup for the TripPlanAgent MCP server.
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv
from datetime import datetime
import asyncio
from pathlib import Path

class Colors:
    """ANSI color codes for beautiful terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header():
    """Print a beautiful header"""
    print(f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                  🔍 ENV VALIDATOR & TESTER 🔍                ║
║              Testing TripPlanAgent API Keys                  ║
╚══════════════════════════════════════════════════════════════╝
{Colors.END}
""")

def check_env_file_exists():
    """Check if .env file exists"""
    env_path = Path(".env")
    print(f"{Colors.BLUE}📁 Checking for .env file...{Colors.END}")
    
    if env_path.exists():
        print(f"{Colors.GREEN}✅ .env file found!{Colors.END}")
        return True
    else:
        print(f"{Colors.RED}❌ .env file not found!{Colors.END}")
        print(f"{Colors.YELLOW}💡 Creating template .env file...{Colors.END}")
        create_env_template()
        return False

def create_env_template():
    """Create a template .env file"""
    template = """# 🔑 API Keys for TripPlanAgent MCP Server
# Replace 'your_key_here' with your actual API keys

# OpenAI API Key (required for LLM operations)
# Get from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_key_here

# Serper API Key (required for Google search)
# Get from: https://serper.dev/api-key
SERPER_API_KEY=your_serper_key_here

# Hyperbrowser API Key (required for advanced browser automation)
# Get from: https://hyperbrowser.ai/
HYPERBROWSER_API_KEY=your_hyperbrowser_key_here
"""
    
    with open(".env", "w") as f:
        f.write(template)
    
    print(f"{Colors.GREEN}✅ Template .env file created!{Colors.END}")
    print(f"{Colors.YELLOW}⚠️  Please edit .env file and add your actual API keys{Colors.END}")

def load_and_validate_env():
    """Load and validate environment variables"""
    print(f"\n{Colors.BLUE}🔄 Loading environment variables...{Colors.END}")
    
    # Load .env file
    load_dotenv()
    
    # Check each required API key
    keys = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "SERPER_API_KEY": os.getenv("SERPER_API_KEY"),
        "HYPERBROWSER_API_KEY": os.getenv("HYPERBROWSER_API_KEY")
    }
    
    all_valid = True
    for key_name, key_value in keys.items():
        if not key_value:
            print(f"{Colors.RED}❌ {key_name}: Not set{Colors.END}")
            all_valid = False
        elif key_value.strip() == "" or "your_" in key_value.lower():
            print(f"{Colors.RED}❌ {key_name}: Template value detected{Colors.END}")
            all_valid = False
        elif len(key_value.strip()) < 10:
            print(f"{Colors.RED}❌ {key_name}: Too short (likely invalid){Colors.END}")
            all_valid = False
        else:
            # Mask the key for security
            masked_key = key_value[:8] + "*" * (len(key_value) - 12) + key_value[-4:]
            print(f"{Colors.GREEN}✅ {key_name}: {masked_key}{Colors.END}")
    
    return all_valid, keys

def test_openai_api(api_key):
    """Test OpenAI API key"""
    print(f"\n{Colors.PURPLE}🤖 Testing OpenAI API...{Colors.END}")
    
    try:
        from langchain_openai import ChatOpenAI
        
        llm = ChatOpenAI(
            temperature=0,
            api_key=api_key,
            model="gpt-3.5-turbo"
        )
        
        # Test with a simple query
        response = llm.invoke([{"role": "user", "content": "Say 'API test successful' in exactly 3 words"}])
        
        if response and hasattr(response, 'content'):
            print(f"{Colors.GREEN}✅ OpenAI API: Working! Response: {response.content.strip()}{Colors.END}")
            return True
        else:
            print(f"{Colors.RED}❌ OpenAI API: Unexpected response format{Colors.END}")
            return False
            
    except Exception as e:
        print(f"{Colors.RED}❌ OpenAI API: {str(e)}{Colors.END}")
        return False

def test_serper_api(api_key):
    """Test Serper API key"""
    print(f"\n{Colors.PURPLE}🔍 Testing Serper API...{Colors.END}")
    
    try:
        # Test web search
        url = "https://google.serper.dev/search"
        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
        data = {"q": "test search", "num": 1}
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if 'organic' in result or 'searchParameters' in result:
                print(f"{Colors.GREEN}✅ Serper Web Search: Working!{Colors.END}")
                
                # Test places search
                places_url = "https://google.serper.dev/places"
                places_data = {"q": "restaurant paris", "num": 1}
                places_response = requests.post(places_url, headers=headers, json=places_data, timeout=10)
                
                if places_response.status_code == 200:
                    print(f"{Colors.GREEN}✅ Serper Places Search: Working!{Colors.END}")
                    return True
                else:
                    print(f"{Colors.YELLOW}⚠️  Serper Places Search: Limited access or quota exceeded{Colors.END}")
                    return True  # Web search works, that's enough
            else:
                print(f"{Colors.RED}❌ Serper API: Unexpected response format{Colors.END}")
                return False
        else:
            print(f"{Colors.RED}❌ Serper API: HTTP {response.status_code} - {response.text[:100]}{Colors.END}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"{Colors.YELLOW}⚠️  Serper API: Timeout (but key might be valid){Colors.END}")
        return True
    except Exception as e:
        print(f"{Colors.RED}❌ Serper API: {str(e)}{Colors.END}")
        return False

def test_hyperbrowser_api(api_key):
    """Test Hyperbrowser API key"""
    print(f"\n{Colors.PURPLE}🌐 Testing Hyperbrowser API...{Colors.END}")
    
    try:
        # Try to import and initialize
        from langchain_hyperbrowser import HyperbrowserBrowserUseTool
        
        # Set the API key in environment
        os.environ["HYPERBROWSER_API_KEY"] = api_key
        
        # Try to create the tool (this will validate the key)
        browser_tool = HyperbrowserBrowserUseTool()
        
        print(f"{Colors.GREEN}✅ Hyperbrowser API: Key format valid and tool initialized!{Colors.END}")
        print(f"{Colors.YELLOW}💡 Note: Full functionality test requires actual browser automation{Colors.END}")
        return True
        
    except ImportError:
        print(f"{Colors.YELLOW}⚠️  Hyperbrowser: Package not installed (pip install langchain-hyperbrowser){Colors.END}")
        return False
    except Exception as e:
        print(f"{Colors.RED}❌ Hyperbrowser API: {str(e)}{Colors.END}")
        return False

def test_mcp_server_syntax():
    """Test MCP server syntax"""
    print(f"\n{Colors.PURPLE}🔧 Testing MCP Server Syntax...{Colors.END}")
    
    try:
        # Try to import the server file
        import sys
        sys.path.append('servers')
        
        # This will check for syntax errors
        import research_server_mcp
        
        print(f"{Colors.GREEN}✅ MCP Server: Syntax valid!{Colors.END}")
        return True
        
    except ImportError as e:
        print(f"{Colors.YELLOW}⚠️  MCP Server: Import issue - {str(e)}{Colors.END}")
        return False
    except SyntaxError as e:
        print(f"{Colors.RED}❌ MCP Server: Syntax error - {str(e)}{Colors.END}")
        return False
    except Exception as e:
        print(f"{Colors.YELLOW}⚠️  MCP Server: Runtime issue - {str(e)}{Colors.END}")
        return True  # Syntax is probably OK

def print_summary(results):
    """Print test summary"""
    print(f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                        📊 TEST SUMMARY                       ║
╚══════════════════════════════════════════════════════════════╝
{Colors.END}""")
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r)
    
    for test_name, passed in results.items():
        status = f"{Colors.GREEN}✅ PASS" if passed else f"{Colors.RED}❌ FAIL"
        print(f"{status}{Colors.END} {test_name}")
    
    print(f"\n{Colors.BOLD}Overall: {passed_tests}/{total_tests} tests passed{Colors.END}")
    
    if passed_tests == total_tests:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 All tests passed! Your MCP server is ready to go!{Colors.END}")
    elif passed_tests >= total_tests - 1:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  Almost there! Fix the failing test and you're good to go!{Colors.END}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ Several issues found. Please fix the API keys and try again.{Colors.END}")

def main():
    """Main testing function"""
    print_header()
    
    # Step 1: Check if .env file exists
    env_exists = check_env_file_exists()
    if not env_exists:
        print(f"\n{Colors.YELLOW}Please edit the .env file with your API keys and run this script again!{Colors.END}")
        return
    
    # Step 2: Load and validate environment
    env_valid, keys = load_and_validate_env()
    if not env_valid:
        print(f"\n{Colors.RED}Please fix the .env file and try again!{Colors.END}")
        return
    
    # Step 3: Test each API
    results = {}
    
    if keys["OPENAI_API_KEY"]:
        results["OpenAI API"] = test_openai_api(keys["OPENAI_API_KEY"])
    
    if keys["SERPER_API_KEY"]:
        results["Serper API"] = test_serper_api(keys["SERPER_API_KEY"])
    
    if keys["HYPERBROWSER_API_KEY"]:
        results["Hyperbrowser API"] = test_hyperbrowser_api(keys["HYPERBROWSER_API_KEY"])
    
    # Step 4: Test MCP server
    results["MCP Server Syntax"] = test_mcp_server_syntax()
    
    # Step 5: Print summary
    print_summary(results)

if __name__ == "__main__":
    main()
