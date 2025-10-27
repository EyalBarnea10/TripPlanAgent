#!/usr/bin/env python3
"""
Test script for Flight Booking MCP Agent
Demonstrates airport search and flight search capabilities
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from servers.flights_booking_mcp import amadeus, format_airport_results, format_flight_results

def test_credentials():
    """Test if Amadeus API credentials are configured"""
    print("🔐 Testing API Credentials...")
    print("-" * 60)
    
    api_key = os.getenv("AMADEUS_API_KEY")
    api_secret = os.getenv("AMADEUS_API_SECRET")
    
    if not api_key or not api_secret:
        print("❌ FAILED: Amadeus API credentials not found")
        print("\n📝 Setup Instructions:")
        print("1. Visit https://developers.amadeus.com/")
        print("2. Register and create a new app")
        print("3. Add to your .env file:")
        print("   AMADEUS_API_KEY=your_api_key")
        print("   AMADEUS_API_SECRET=your_api_secret")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    print(f"✅ API Secret found: {api_secret[:10]}...")
    
    # Test authentication
    try:
        token = amadeus.get_access_token()
        print(f"✅ Authentication successful!")
        print(f"   Access token: {token[:20]}...")
        return True
    except Exception as e:
        print(f"❌ Authentication failed: {str(e)}")
        return False

def test_airport_search():
    """Test airport search functionality"""
    print("\n\n🛫 Testing Airport Search...")
    print("=" * 60)
    
    test_cities = ["Naples", "New York", "Paris"]
    
    for city in test_cities:
        print(f"\n🔍 Searching for airports in: {city}")
        print("-" * 60)
        try:
            results = amadeus.get_airport_info(city)
            formatted = format_airport_results(results)
            print(formatted)
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def test_flight_search():
    """Test flight search functionality"""
    print("\n\n✈️  Testing Flight Search...")
    print("=" * 60)
    
    # Test search: New York to Naples in March
    print("\n🎫 Searching: JFK → NAP (Round Trip)")
    print("   Departure: 2025-03-15")
    print("   Return: 2025-03-22")
    print("   Passengers: 2 adults")
    print("   Class: Economy")
    print("-" * 60)
    
    try:
        results = amadeus.search_flights(
            origin="JFK",
            destination="NAP",
            departure_date="2025-03-15",
            return_date="2025-03-22",
            adults=2,
            travel_class="ECONOMY",
            max_results=5
        )
        
        formatted = format_flight_results(results)
        print(formatted)
        
        # Show pricing summary
        if "data" in results and len(results["data"]) > 0:
            prices = [float(offer["price"]["total"]) for offer in results["data"]]
            print(f"\n💰 PRICE SUMMARY:")
            print(f"   Cheapest: ${min(prices)}")
            print(f"   Average: ${sum(prices)/len(prices):.2f}")
            print(f"   Most expensive: ${max(prices)}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Run all tests"""
    print("="*60)
    print("🧪 FLIGHT BOOKING AGENT TEST SUITE")
    print("="*60)
    
    # Test 1: Credentials
    if not test_credentials():
        print("\n⚠️  Cannot proceed without valid API credentials")
        print("   Please set up your Amadeus API credentials first")
        print("   See FLIGHT_BOOKING_SETUP.md for instructions")
        return
    
    # Test 2: Airport Search
    test_airport_search()
    
    # Test 3: Flight Search
    test_flight_search()
    
    print("\n\n" + "="*60)
    print("✅ TEST SUITE COMPLETE!")
    print("="*60)
    print("\n💡 Next Steps:")
    print("   1. Review the flight results above")
    print("   2. Try different routes and dates")
    print("   3. Use the MCP tools in your AI assistant")
    print("   4. See FLIGHT_BOOKING_SETUP.md for more info")

if __name__ == "__main__":
    main()

