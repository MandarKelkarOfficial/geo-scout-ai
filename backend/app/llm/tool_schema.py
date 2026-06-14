TOOLS = [
    {
        "name": "get_weather",
        "description": "Get current weather information for a specific location.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "The city and state/country, e.g., 'Pune', 'Kharadi'"}
            },
            "required": ["location"]
        }
    },
    {
        "name": "geocode_location",
        "description": "Convert a place name into latitude and longitude coordinates.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "The place name to geocode"}
            },
            "required": ["location"]
        }
    },
    {
        "name": "get_nearby_places",
        "description": "Find nearby places of a specific category like restaurants, hospitals, etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "The center location to search around"},
                "category": {"type": "string", "description": "The type of place to find, e.g., 'restaurant', 'hospital', 'school'"}
            },
            "required": ["location", "category"]
        }
    },
    {
        "name": "get_satellite_info",
        "description": "Get satellite imagery information for a location.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "The location to get satellite info for"}
            },
            "required": ["location"]
        }
    },
    {
        "name": "search_real_estate",
        "description": "Search for real estate listings in a location within a budget.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "The location to search for properties"},
                "min_budget": {"type": "number", "description": "The minimum budget in INR"},
                "max_budget": {"type": "number", "description": "The maximum budget in INR"}
            },
            "required": ["location"]
        }
    }
]
