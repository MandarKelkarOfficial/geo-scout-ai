from abc import ABC, abstractmethod
import re
from app.core.config import get_settings

settings = get_settings()

class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        pass

class MockLLMProvider(BaseLLMProvider):
    async def generate(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        import json

        # Check if the last message is a tool result — synthesize natural language
        last_message = messages[-1] if messages else {}
        if last_message.get("role") == "tool":
            tool_name = last_message.get("name", "")
            raw = last_message.get("content", "")
            try:
                data = json.loads(raw)
            except Exception:
                return {"type": "final_answer", "content": raw}

            if tool_name == "get_weather":
                loc = data.get("location", "the location")
                temp = data.get("temperature_celsius")
                cond = data.get("condition", "Unknown")
                humidity = data.get("humidity")
                wind = data.get("wind_speed_kmh")
                feels = data.get("feels_like_celsius")
                parts = [f"**Current Weather in {loc}**\n"]
                parts.append(f"**Temperature:** {temp}°C" + (f" (feels like {feels}°C)" if feels else ""))
                parts.append(f"**Condition:** {cond}")
                if humidity is not None:
                    parts.append(f"**Humidity:** {humidity}%")
                if wind is not None:
                    parts.append(f"**Wind Speed:** {wind} km/h")
                return {"type": "final_answer", "content": "\n".join(parts)}

            elif tool_name == "get_nearby_places":
                places = data.get("places", [])
                # category is on each PlaceResult item, not top-level
                category = places[0].get("category", "places") if places else "places"
                if not places:
                    return {"type": "final_answer", "content": f"I couldn't find any {category} nearby. The area may not have mapped results yet."}
                lines = [f"**Nearby {category.title()}**\n"]
                for idx, p in enumerate(places[:8], 1):
                    name = p.get("name", "Unnamed")
                    dist_m = p.get("distance_meters")
                    lat_p = p.get("latitude")
                    lon_p = p.get("longitude")
                    line = f"{idx}. **{name}**"
                    if dist_m is not None:
                        dist_km = dist_m / 1000 if dist_m > 100 else dist_m
                        line += f" — {dist_km:.2f} km away"
                    if lat_p and lon_p:
                        line += f"\n   {lat_p:.4f}°N, {lon_p:.4f}°E"
                    lines.append(line)
                return {"type": "final_answer", "content": "\n".join(lines)}

            elif tool_name == "search_real_estate":
                listings = data.get("listings", [])
                # location is on each listing item in this schema
                location = listings[0].get("location", "") if listings else ""
                budget_max = None
                if not listings:
                    return {"type": "final_answer", "content": f"No property listings found matching your budget."}
                budget_str = ""
                if budget_max:
                    budget_str = f" under ₹{int(budget_max/100000)}L"
                lines = [f"**Real Estate Listings in {location}{budget_str}**\n"]
                for i, l in enumerate(listings[:6], 1):
                    title = l.get("title", "Property")
                    price = l.get("price", 0)
                    area = l.get("area_sqft")
                    dealer = l.get("dealer_name", "")
                    price_str = f"₹{int(price/100000)}L" if price >= 100000 else f"₹{int(price)}"
                    line = f"{i}. **{title}** — {price_str}"
                    if area:
                        line += f" | {area} sq.ft"
                    if dealer:
                        line += f"\n   {dealer}"
                    lines.append(line)
                return {"type": "final_answer", "content": "\n".join(lines)}

            elif tool_name == "geocode_location":
                name = data.get("display_name", "")
                lat = data.get("latitude")
                lon = data.get("longitude")
                lines = [f"**Location Found**\n"]
                lines.append(f"**{name}**")
                if lat and lon:
                    lines.append(f"Coordinates: {lat:.5f}°N, {lon:.5f}°E")
                return {"type": "final_answer", "content": "\n".join(lines)}

            # Fallback for unknown tools
            return {"type": "final_answer", "content": str(raw)}

        # Otherwise, process the latest user query
        query = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                query = msg.get("content", "").lower()
                break

        if "weather" in query or "temperature" in query:
            match = re.search(r'in (.*)', query)
            loc = match.group(1).strip().strip('?') if match else "Pune"
            return {
                "type": "tool_call",
                "tool": "get_weather",
                "arguments": {"location": loc}
            }
        elif any(word in query for word in ["house", "buy", "rent", "property"]):
            match = re.search(r'in ([\w\s]+)', query + " ")
            loc = match.group(1).strip() if match else "Kharadi"
            
            # Simple budget extraction (assuming lakhs)
            budget_match = re.findall(r'\b\d+(?:\.\d+)?\b', query)
            min_b, max_b = None, None
            if len(budget_match) >= 2:
                min_b = float(budget_match[0]) * 100000
                max_b = float(budget_match[1]) * 100000
            elif len(budget_match) == 1:
                max_b = float(budget_match[0]) * 100000
            
            args = {"location": loc}
            if min_b: args["min_budget"] = min_b
            if max_b: args["max_budget"] = max_b
                
            return {
                "type": "tool_call",
                "tool": "search_real_estate",
                "arguments": args
            }
        elif "near" in query or "nearby" in query:
            match = re.search(r'(.*?) near (.*)', query)
            if match:
                cat = match.group(1).replace("find", "").replace("search", "").strip()
                loc = match.group(2).strip().strip('?')
            else:
                cat = "restaurant"
                loc = "Pune"
            return {
                "type": "tool_call",
                "tool": "get_nearby_places",
                "arguments": {"location": loc, "category": cat}
            }
        
        return {
            "type": "final_answer",
            "content": "I can help you with weather, places, and real estate!"
        }

def get_llm_provider() -> BaseLLMProvider:
    provider = settings.LLM_PROVIDER.lower()
    if provider == "mock":
        return MockLLMProvider()
    raise NotImplementedError(f"LLM provider '{provider}' is not implemented.")
