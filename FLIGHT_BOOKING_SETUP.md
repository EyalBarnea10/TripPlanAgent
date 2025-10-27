# Flight Booking Agent Setup Guide

## 🛫 Overview

The Flight Booking MCP Agent uses the **Amadeus API** - one of the world's leading travel technology platforms used by airlines, travel agencies, and booking platforms globally.

## 🚀 Quick Setup

### Step 1: Get Amadeus API Credentials

1. Visit [Amadeus for Developers](https://developers.amadeus.com/)
2. Click **Register** (free account)
3. Verify your email
4. Log in to your dashboard
5. Click **Create New App**
6. Choose **Self-Service** (free tier)
7. Give your app a name (e.g., "TripPlanAgent")
8. Copy your **API Key** and **API Secret**

### Step 2: Configure Environment Variables

Add to your `.env` file:

```env
# Amadeus API Credentials
AMADEUS_API_KEY=your_api_key_here
AMADEUS_API_SECRET=your_api_secret_here

# Existing credentials
OPENAI_API_KEY=your_openai_key
SERPER_API_KEY=your_serper_key
```

### Step 3: Test the Setup

Run the test script:

```bash
python test_flight_booking.py
```

## 🎯 Usage Examples

### Find Airport Codes

```python
# Find airports in Naples
find_airports("Naples")

# Result:
# 📍 Naples International Airport (NAP)
#    Location: Naples, Italy
```

### Search Flights

```python
# Search round-trip flights
search_flights(
    origin="JFK",           # New York JFK
    destination="NAP",      # Naples
    departure_date="2025-03-15",
    return_date="2025-03-22",
    adults=2,
    travel_class="ECONOMY"
)
```

### Common Routes for Naples Trip

```bash
# From New York
JFK (or EWR, LGA) → NAP

# From Los Angeles
LAX → NAP

# From London
LHR (or LGW, STN) → NAP

# From Paris
CDG → NAP
```

## 📊 API Limits & Pricing

### Free Tier (Test API)
- ✅ **Unlimited** API calls for testing
- ✅ Flight search and pricing
- ✅ Airport/city search
- ❌ Cannot make actual bookings (test data only)

### Production Tier
- 💰 **2,000 free** API calls/month
- 💰 Then $0.35 per API call
- ✅ Real flight data
- ✅ Actual booking capabilities
- ✅ Payment processing

## 🎫 Travel Class Options

- `ECONOMY` - Standard economy class
- `PREMIUM_ECONOMY` - Extra legroom and amenities
- `BUSINESS` - Business class
- `FIRST` - First class (luxury)

## 🌍 Supported Features

✅ **One-way flights**
✅ **Round-trip flights**
✅ **Multi-city trips**
✅ **Flexible passenger count**
✅ **Class preferences**
✅ **400+ airlines worldwide**
✅ **Real-time pricing**
✅ **190+ countries**

## 💡 Best Practices

### Booking Tips
- 📅 Book 2-3 months in advance for best prices
- 🗓️ Tuesday/Wednesday are often cheapest
- 🕐 Early morning and late evening flights are usually cheaper
- 🔄 Use flexible dates if possible

### For Naples (March)
- 🌡️ Mild weather (10-16°C)
- 👥 Less crowded than summer
- 💰 Good deals available (off-peak season)
- ✈️ Consider flying into Rome (FCO) as alternative

## 🔧 Troubleshooting

### Error: "Authentication failed"
- Check your API key and secret in `.env`
- Verify credentials are active in Amadeus dashboard
- Make sure there are no extra spaces in the `.env` file

### Error: "No flights found"
- Verify airport codes are valid 3-letter IATA codes
- Check dates are in the future
- Try different dates or nearby airports
- Ensure date format is YYYY-MM-DD

### Error: "Airport code not found"
- Use `find_airports()` tool first
- Try searching by city name
- Check for typos in airport codes

## 📚 Additional Resources

- [Amadeus API Documentation](https://developers.amadeus.com/self-service/category/flights)
- [API Reference](https://developers.amadeus.com/self-service/apis-docs)
- [Community Forum](https://developers.amadeus.com/support/forum)
- [Code Examples](https://github.com/amadeus4dev)

## 🎯 Integration with TripPlanAgent

The Flight Booking Agent is **Phase 2** of the complete trip planning system:

1. **Phase 1**: Use `research_server_mcp.py` to research Naples destinations, hotels, activities
2. **Phase 2**: Use `flights_booking_mcp.py` to find and book flights
3. **Phase 3**: (Future) Complete booking, itinerary generation, document management

## 🔮 Future Enhancements

- [ ] Direct booking capability
- [ ] Hotel + Flight packages
- [ ] Car rental integration
- [ ] Travel insurance options
- [ ] Price tracking and alerts
- [ ] Multi-stop itinerary optimization
- [ ] Loyalty program integration

## 🆘 Support

For issues or questions:
1. Check the [FLIGHT_BOOKING_SETUP.md](./FLIGHT_BOOKING_SETUP.md) guide
2. Review Amadeus [documentation](https://developers.amadeus.com/)
3. Open an issue in the repository

---

**Built with ❤️ using Amadeus API and Model Context Protocol**

