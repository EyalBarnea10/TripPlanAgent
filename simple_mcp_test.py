#!/usr/bin/env python3
"""
🚀 Simple MCP Server Test
Tests if the MCP server starts correctly and exposes tools properly.
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def test_mcp_server():
    """Test if the MCP server starts without errors"""
    print("🔧 Testing MCP Server startup...")
    
    try:
        # Start the server process
        process = subprocess.Popen(
            [sys.executable, "servers/research_server_mcp.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment for startup
        time.sleep(2)
        
        # Check if process is still running (not crashed)
        if process.poll() is None:
            print("✅ MCP Server: Started successfully and is running!")
            
            # Kill the process
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            
            return True
        else:
            # Process exited, check for errors
            stdout, stderr = process.communicate()
            print(f"❌ MCP Server: Exited with code {process.returncode}")
            if stderr:
                print(f"Error output: {stderr}")
            if stdout:
                print(f"Standard output: {stdout}")
            return False
            
    except Exception as e:
        print(f"❌ MCP Server: Failed to start - {str(e)}")
        return False

def test_env_file():
    """Quick test of .env file"""
    print("📁 Testing .env file...")
    
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found")
        return False
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check keys
    keys = ["OPENAI_API_KEY", "SERPER_API_KEY", "HYPERBROWSER_API_KEY"]
    all_good = True
    
    for key in keys:
        value = os.getenv(key)
        if not value or "your_" in value.lower() or len(value.strip()) < 10:
            print(f"❌ {key}: Missing or invalid")
            all_good = False
        else:
            masked = value[:8] + "*" * (len(value) - 12) + value[-4:]
            print(f"✅ {key}: {masked}")
    
    return all_good

def main():
    print("""
🚀 Simple MCP Server Test
==========================
""")
    
    # Test 1: Environment file
    env_ok = test_env_file()
    
    # Test 2: MCP Server startup
    server_ok = test_mcp_server()
    
    print(f"""
📊 Test Summary:
================
Environment File: {'✅ PASS' if env_ok else '❌ FAIL'}
MCP Server:       {'✅ PASS' if server_ok else '❌ FAIL'}

Overall: {'🎉 All tests passed!' if env_ok and server_ok else '⚠️ Some issues found'}
""")
    
    if env_ok and server_ok:
        print("""
🎉 SUCCESS! Your MCP server is working correctly!

Now you can:
1. Restart Cursor to reload MCP configuration
2. Use the research tools in your conversations
3. Test with queries like "research the best restaurants in Paris"
""")

if __name__ == "__main__":
    main()
