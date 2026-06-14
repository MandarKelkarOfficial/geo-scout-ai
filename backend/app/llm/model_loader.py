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
        # Check if the last message is a tool result
        last_message = messages[-1] if messages else {}
        if last_message.get("role") == "tool":
            return {
                "type": "final_answer",
                "content": f"Based on the tool results: {last_message.get('content')}"
            }

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
