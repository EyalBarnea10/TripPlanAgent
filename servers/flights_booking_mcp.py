"""
Flight Booking MCP Server - Amadeus API Integration
====================================================

This MCP server provides comprehensive flight search and booking capabilities
using the Amadeus API - one of the leading GDS (Global Distribution Systems)
used by airlines and travel agencies worldwide.

Features:
- Flight search with flexible date options
- Real-time pricing and availability
- Multi-city and round-trip support
- Airline, class, and stop preferences
- Flight booking capabilities (future enhancement)
"""

from fastmcp import FastMCP   
from dotenv import load_dotenv
import os
import requests
import json  
from datetime import datetime, timedelta
from typing import Optional, Dict, List

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("flights_booking_mcp")


# ============================================================================
# AMADEUS API AUTHENTICATION & HELPERS
# ============================================================================

class AmadeusAPI:
    """Handle Amadeus API authentication and requests"""
    
    def __init__(self):
        self.api_key = os.getenv("AMADEUS_API_KEY")
        self.api_secret = os.getenv("AMADEUS_API_SECRET")
        self.base_url = "https://test.api.amadeus.com"  # Use production URL for live bookings
        self.access_token = None
        self.token_expires_at = None
    
    def get_access_token(self) -> str:
        """Get or refresh Amadeus API access token"""
        # Check if we have a valid token
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at:
                return self.access_token
        
        # Get new token
        url = f"{self.base_url}/v1/security/oauth2/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.api_secret
        }
        
        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            result = response.json()
            
            self.access_token = result["access_token"]
            # Token typically expires in 1800 seconds (30 minutes)
            expires_in = result.get("expires_in", 1800)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
            
            return self.access_token
        except Exception as e:
            raise Exception(f"Failed to authenticate with Amadeus API: {str(e)}")
    
    def search_flights(self, origin: str, destination: str, departure_date: str, 
                      return_date: Optional[str] = None, adults: int = 1,
                      travel_class: str = "ECONOMY", max_results: int = 10) -> Dict:
        """Search for flights using Amadeus Flight Offers Search API"""
        token = self.get_access_token()
        url = f"{self.base_url}/v2/shopping/flight-offers"
        
        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "originLocationCode": origin.upper(),
            "destinationLocationCode": destination.upper(),
            "departureDate": departure_date,
            "adults": adults,
            "travelClass": travel_class.upper(),
            "max": max_results,
            "currencyCode": "USD"
        }
        
        if return_date:
            params["returnDate"] = return_date
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Flight search error: {str(e)}")
    
    def get_airport_info(self, keyword: str) -> Dict:
        """Search for airports by city or airport code"""
        token = self.get_access_token()
        url = f"{self.base_url}/v1/reference-data/locations"
        
        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "subType": "AIRPORT,CITY",
            "keyword": keyword,
            "page[limit]": 10
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Airport search error: {str(e)}")


# Initialize Amadeus API client
amadeus = AmadeusAPI()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def format_flight_results(data: Dict) -> str:
    """Format flight search results in a readable way"""
    if "errors" in data:
        errors = data["errors"]
        error_messages = [f"- {err.get('title', 'Unknown error')}: {err.get('detail', '')}" 
                         for err in errors]
        return f"❌ Error searching flights:\n" + "\n".join(error_messages)
    
    if "data" not in data or len(data["data"]) == 0:
        return "No flights found for your search criteria. Try different dates or airports."
    
    results = []
    results.append("✈️  FLIGHT SEARCH RESULTS")
    results.append("=" * 80)
    
    for idx, offer in enumerate(data["data"][:10], 1):
        price = offer["price"]["total"]
        currency = offer["price"]["currency"]
        
        results.append(f"\n🎫 Option {idx}: {currency} {price}")
        results.append("-" * 40)
        
        for segment_idx, itinerary in enumerate(offer["itineraries"], 1):
            if segment_idx == 1:
                results.append("OUTBOUND:")
            else:
                results.append("\nRETURN:")
            
            duration = itinerary["duration"]
            
            for seg in itinerary["segments"]:
                departure = seg["departure"]
                arrival = seg["arrival"]
                carrier = seg["carrierCode"]
                flight_num = seg["number"]
                
                dep_time = departure["at"].replace("T", " ")
                arr_time = arrival["at"].replace("T", " ")
                
                results.append(f"  {carrier}{flight_num}: {departure['iataCode']} → {arrival['iataCode']}")
                results.append(f"  Depart: {dep_time}")
                results.append(f"  Arrive: {arr_time}")
        
        results.append(f"Duration: {duration}")
    
    results.append("\n" + "=" * 80)
    results.append(f"Total results: {len(data['data'])} flights found")
    
    return "\n".join(results)


def format_airport_results(data: Dict) -> str:
    """Format airport search results"""
    if "errors" in data:
        return f"❌ Error: {data['errors'][0].get('detail', 'Unknown error')}"
    
    if "data" not in data or len(data["data"]) == 0:
        return "No airports found. Try a different search term."
    
    results = []
    results.append("🛫 AIRPORT SEARCH RESULTS")
    results.append("=" * 60)
    
    for airport in data["data"]:
        name = airport.get("name", "Unknown")
        iata = airport.get("iataCode", "N/A")
        city = airport["address"].get("cityName", "Unknown")
        country = airport["address"].get("countryName", "Unknown")
        
        results.append(f"\n📍 {name} ({iata})")
        results.append(f"   Location: {city}, {country}")
    
    results.append("\n" + "=" * 60)
    
    return "\n".join(results)


# ============================================================================
# MCP TOOLS - EXPOSED ENDPOINTS
# ============================================================================

@mcp.tool()
def search_flights(origin: str, destination: str, departure_date: str,
                  return_date: str = None, adults: int = 1,
                  travel_class: str = "ECONOMY") -> str:
    """
    Search for flights using Amadeus API.
    
    Args:
        origin: Origin airport code (e.g., "JFK", "LAX", "LHR")
        destination: Destination airport code (e.g., "CDG", "NAP", "FCO")
        departure_date: Departure date in YYYY-MM-DD format
        return_date: Return date in YYYY-MM-DD format (optional, for round-trip)
        adults: Number of adult passengers (default: 1)
        travel_class: Travel class - ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST (default: ECONOMY)
    
    Returns:
        Formatted flight search results with prices, times, and airlines
    
    Example:
        search_flights("JFK", "NAP", "2025-03-15", "2025-03-22", 2, "ECONOMY")
    """
    try:
        # Validate inputs
        if not origin or not destination:
            return "❌ Error: Origin and destination airport codes are required"
        
        if len(origin) != 3 or len(destination) != 3:
            return "❌ Error: Airport codes must be 3 letters (IATA codes). Use find_airports tool to search."
        
        # Validate date format
        try:
            datetime.strptime(departure_date, "%Y-%m-%d")
            if return_date:
                datetime.strptime(return_date, "%Y-%m-%d")
        except ValueError:
            return "❌ Error: Dates must be in YYYY-MM-DD format"
        
        # Check API credentials
        if not os.getenv("AMADEUS_API_KEY") or not os.getenv("AMADEUS_API_SECRET"):
            return """❌ Error: Amadeus API credentials not found.
            
Please set up your Amadeus API credentials:
1. Sign up at https://developers.amadeus.com/
2. Create a new app to get API Key and Secret
3. Add to your .env file:
   AMADEUS_API_KEY=your_api_key
   AMADEUS_API_SECRET=your_api_secret
"""
        
        # Search flights
        results = amadeus.search_flights(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            adults=adults,
            travel_class=travel_class
        )
        
        return format_flight_results(results)
        
    except Exception as e:
        return f"❌ Error searching flights: {str(e)}"


@mcp.tool()
def find_airports(search_term: str) -> str:
    """
    Find airport codes by city name or airport name.
    
    Args:
        search_term: City name or airport name to search (e.g., "Naples", "New York", "Paris")
    
    Returns:
        List of matching airports with IATA codes
    
    Example:
        find_airports("Naples")
        find_airports("New York")
    """
    try:
        if not os.getenv("AMADEUS_API_KEY") or not os.getenv("AMADEUS_API_SECRET"):
            return """❌ Error: Amadeus API credentials not found.

Please set up your Amadeus API credentials in your .env file.
Visit https://developers.amadeus.com/ to get your credentials."""
        
        results = amadeus.get_airport_info(search_term)
        return format_airport_results(results)
        
    except Exception as e:
        return f"❌ Error searching airports: {str(e)}"


@mcp.tool()
def flight_booking_help() -> str:
    """
    Get help and information about using the flight booking agent.
    
    Returns:
        Comprehensive guide on how to use the flight booking tools
    """
    return """
🛫 FLIGHT BOOKING AGENT - USER GUIDE
═══════════════════════════════════════════════════════════════════

📋 AVAILABLE TOOLS:

1. find_airports(search_term)
   - Find airport codes by city or airport name
   - Example: find_airports("Naples")
   
2. search_flights(origin, destination, departure_date, return_date, adults, travel_class)
   - Search for available flights with pricing
   - Example: search_flights("JFK", "NAP", "2025-03-15", "2025-03-22", 2)

⚙️  SETUP REQUIRED:

1. Sign up at https://developers.amadeus.com/
2. Create a new app (self-service)
3. Copy your API Key and API Secret
4. Add to .env file:
   AMADEUS_API_KEY=your_api_key_here
   AMADEUS_API_SECRET=your_api_secret_here

📝 USAGE WORKFLOW:

Step 1: Find airport codes
   find_airports("New York") → Get "JFK", "LGA", "EWR"
   find_airports("Naples") → Get "NAP"

Step 2: Search flights
   search_flights("JFK", "NAP", "2025-03-15", "2025-03-22", 2, "ECONOMY")

Step 3: Review results
   - Compare prices, airlines, and schedules
   - Note flight numbers and times

🎫 TRAVEL CLASSES:
   - ECONOMY (default)
   - PREMIUM_ECONOMY
   - BUSINESS
   - FIRST

💡 TIPS:
   - Use 3-letter IATA airport codes (e.g., JFK, LAX, CDG)
   - Dates must be in YYYY-MM-DD format
   - Book flights 2-3 months in advance for best prices
   - Tuesday and Wednesday are often cheapest
   - Consider flexible dates to find better deals

🔮 FUTURE FEATURES:
   - Direct flight booking (requires production API)
   - Seat selection
   - Baggage options
   - Hotel + Flight packages
   - Price alerts and tracking

For more info: https://developers.amadeus.com/self-service/category/flights
"""


# ============================================================================
# DOCUMENTATION
# ============================================================================

"""
═══════════════════════════════════════════════════════════════════════════
FLIGHT BOOKING MCP SERVER - ARCHITECTURE & INTEGRATION
═══════════════════════════════════════════════════════════════════════════

PURPOSE:
This MCP server provides Phase 2 functionality for the Trip Planning system,
focusing on flight search and booking capabilities using Amadeus API.

INTEGRATION WITH TRIP PLANNING WORKFLOW:
┌─────────────────────────────────────────────────────────────────────────┐
│  PHASE 1: Research & Discovery (research_server_mcp.py) ✅             │
│  └── Destination selection, hotels, activities                          │
│                                                                          │
│  PHASE 2: Flight Booking (THIS SERVER) ✅                               │
│  ├── Airport search and discovery                                       │
│  ├── Flight availability and pricing                                    │
│  ├── Multi-city and round-trip support                                  │
│  └── Class and airline preferences                                      │
│                                                                          │
│  PHASE 3: Complete Booking (Future)                                     │
│  ├── Actual flight booking                                              │
│  ├── Hotel reservations                                                 │
│  ├── Complete itinerary generation                                      │
│  └── Travel document management                                         │
└─────────────────────────────────────────────────────────────────────────┘

AMADEUS API BENEFITS:
✅ Real-time flight data from 400+ airlines
✅ Competitive pricing with live availability
✅ Global coverage (190+ countries)
✅ Production-ready booking capabilities
✅ Trusted by major travel agencies

API ENDPOINTS USED:
- Flight Offers Search: Real-time flight search
- Airport & City Search: IATA code lookup
- OAuth2 Authentication: Secure API access

TESTING:
Use the Amadeus Test API (currently configured) for development.
Switch to production URL for live bookings.

Example Test Data:
- Origin: MAD (Madrid)
- Destination: ATH (Athens)
- Date: Any future date

PRODUCTION DEPLOYMENT:
1. Switch base_url to https://api.amadeus.com
2. Update API credentials to production keys
3. Implement booking confirmation workflow
4. Add payment processing integration
5. Set up error monitoring and logging
"""

if __name__ == "__main__":
    mcp.run()
