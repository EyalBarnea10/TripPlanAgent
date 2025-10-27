#!/usr/bin/env python3
"""
Naples Trip Research - Using Direct API Calls
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def search_google_serper(query, endpoint="search"):
    """Direct call to Serper API"""
    serper_key = os.getenv("SERPER_API_KEY")
    url = f"https://google.serper.dev/{endpoint}"
    headers = {
        'X-API-KEY': serper_key,
        'Content-Type': 'application/json'
    }
    data = json.dumps({"q": query})
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def optimize_query_openai(query):
    """Optimize query using OpenAI"""
    api_key = os.getenv("OPENAI_API_KEY")
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "You are a travel search expert. Optimize queries for Google search. Return ONLY the optimized query."},
            {"role": "user", "content": f'Optimize this travel query: "{query}"'}
        ],
        "temperature": 0
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    except Exception as e:
        return query  # Return original if optimization fails

def main():
    print("🇮🇹 NAPLES FAMILY TRIP - MARCH 2025")
    print("=" * 80)
    print("👨‍👩‍👧‍👦 Travelers: Adults + 2 Teenagers")
    print("=" * 80)
    print()
    
    # Check API keys
    if not os.getenv("SERPER_API_KEY") or not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: Missing API keys in .env file")
        print("   Need: OPENAI_API_KEY and SERPER_API_KEY")
        return
    
    query = "Naples Italy family trip March teenagers best attractions restaurants hotels teen activities"
    
    print("🔍 Step 1: Optimizing search query...")
    optimized = optimize_query_openai(query)
    print(f"✨ Optimized: {optimized}\n")
    
    print("=" * 80)
    print("📰 WEB SEARCH RESULTS - Travel Guides & Tips")
    print("=" * 80)
    web_results = search_google_serper(optimized, "search")
    
    if 'organic' in web_results:
        for i, result in enumerate(web_results['organic'][:8], 1):
            print(f"\n{i}. {result.get('title', 'N/A')}")
            print(f"   🔗 {result.get('link', 'N/A')}")
            print(f"   📝 {result.get('snippet', 'N/A')[:150]}...")
    elif 'error' in web_results:
        print(f"Error: {web_results['error']}")
    
    print("\n\n" + "=" * 80)
    print("📍 PLACES SEARCH - Hotels, Restaurants & Attractions")
    print("=" * 80)
    places_results = search_google_serper("Naples Italy hotels restaurants attractions for families", "places")
    
    if 'places' in places_results:
        for i, place in enumerate(places_results['places'][:10], 1):
            print(f"\n{i}. {place.get('title', 'N/A')}")
            rating = place.get('rating', 'N/A')
            reviews = place.get('ratingCount', 0)
            print(f"   ⭐ {rating} ({reviews} reviews)")
            print(f"   📍 {place.get('address', 'N/A')}")
            if place.get('category'):
                print(f"   🏷️  {place.get('category')}")
    elif 'error' in places_results:
        print(f"Error: {places_results['error']}")
    
    print("\n\n" + "=" * 80)
    print("💡 NAPLES IN MARCH - QUICK TIPS")
    print("=" * 80)
    print("""
🌡️  WEATHER: Mild (10-16°C / 50-61°F) - Pack layers!
👥 CROWDS: Much less crowded than summer
🎯 TEEN-FRIENDLY ACTIVITIES:
   • Pizza-making workshop (Naples invented pizza!)
   • Underground Naples tour (Napoli Sotterranea)
   • Street art tour in Quartieri Spagnoli
   • Arcade and gaming at Centro Commerciale Campania
   
🏛️  TOP ATTRACTIONS:
   • Pompeii & Herculaneum (must-see ancient ruins!)
   • Mount Vesuvius hike
   • Naples Archaeological Museum
   • Castel dell'Ovo & waterfront
   • Spaccanapoli historic street
   
🍕 FOOD EXPERIENCES:
   • L'Antica Pizzeria da Michele (original pizzeria)
   • Di Matteo (Anthony Bourdain's favorite)
   • Sfogliatella at Attanasio
   • Gelato at Gay-Odin chocolate factory
   
🚗 DAY TRIPS:
   • Amalfi Coast (Positano, Amalfi, Ravello)
   • Capri Island (Blue Grotto, chairlift)
   • Sorrento
   • Procida Island (colorful & less touristy)
   
🏨 WHERE TO STAY:
   • Centro Storico: Best for sightseeing walkability
   • Vomero: Upscale, quieter neighborhood
   • Chiaia: Beach area, shopping, restaurants
   
⚠️  TIPS:
   • Book Pompeii tickets online in advance
   • Watch belongings in crowded areas
   • Try the metro art stations (Toledo station is stunning!)
   • Learn a few Italian phrases - locals appreciate it!
    """)
    
    print("=" * 80)
    print("✅ RESEARCH COMPLETE! Buon viaggio! 🇮🇹")
    print("=" * 80)

if __name__ == "__main__":
    main()

