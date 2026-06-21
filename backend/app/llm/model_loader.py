import json
import re
import httpx
import structlog
from abc import ABC, abstractmethod
from app.core.config import get_settings

settings = get_settings()
logger = structlog.get_logger()


class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        pass


# ---------------------------------------------------------------------------
# OllamaLLMProvider — calls local Ollama (http://localhost:11434)
# Uses the /api/chat endpoint with native tool-calling support.
# Compatible with qwen2.5-coder:1.5b and other Ollama models.
# ---------------------------------------------------------------------------

class OllamaLLMProvider(BaseLLMProvider):
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.LLM_MODEL_NAME
        self.timeout = settings.LLM_TIMEOUT_SECONDS

    def _convert_tools_to_ollama_format(self, tools: list[dict]) -> list[dict]:
        """Convert our internal tool schema to Ollama's expected format."""
        ollama_tools = []
        for tool in tools:
            ollama_tools.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool.get("parameters", {})
                }
            })
        return ollama_tools

    def _convert_messages_for_ollama(self, messages: list[dict]) -> list[dict]:
        """
        Adapt our internal message format to Ollama's chat format.
        qwen2.5-coder works best when tool results are presented as
        a user turn so it knows to synthesize a natural language response.
        """
        converted = []
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")

            if role == "tool":
                # Present tool result as a user message for qwen2.5-coder
                # so the model synthesizes a natural language answer.
                tool_name = msg.get("name", "tool")
                converted.append({
                    "role": "user",
                    "content": (
                        f"[Tool result from {tool_name}]\n"
                        f"{content}\n\n"
                        f"Now give a clear, helpful, conversational answer to the original question using this data."
                    )
                })
            elif role == "assistant" and content is None:
                # Skip assistant messages that were just tool-call placeholders
                pass
            elif role in ("system", "user", "assistant"):
                if content:  # skip empty content messages
                    converted.append({"role": role, "content": content})
        return converted

    async def generate(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        payload = {
            "model": self.model,
            "messages": self._convert_messages_for_ollama(messages),
            "stream": False,
        }

        if tools:
            payload["tools"] = self._convert_tools_to_ollama_format(tools)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as e:
            logger.error("ollama_api_error", error=str(e))
            return {"type": "final_answer", "content": f"[LLM Error] Could not reach Ollama: {e}"}

        message = data.get("message", {})
        content = message.get("content", "").strip()

        # --- Path 1: Native tool_calls in the message (full Ollama tool-call support) ---
        tool_calls = message.get("tool_calls")
        if tool_calls and len(tool_calls) > 0:
            first_call = tool_calls[0]
            func = first_call.get("function", {})
            tool_name = func.get("name", "")
            raw_args = func.get("arguments", {})
            if isinstance(raw_args, str):
                try:
                    args = json.loads(raw_args)
                except json.JSONDecodeError:
                    args = {}
            else:
                args = raw_args
            logger.info("ollama_tool_call_native", tool=tool_name, args=args)
            return {"type": "tool_call", "tool": tool_name, "arguments": args}

        # --- Path 2: qwen2.5-coder outputs JSON tool call inside content string ---
        # The model may produce bare JSON or wrap it in markdown: ```json {...} ```
        stripped = content
        if stripped.startswith("```"):
            # Remove opening fence (```json or just ```)
            stripped = stripped.split("\n", 1)[-1] if "\n" in stripped else stripped
            # Remove closing fence
            if stripped.endswith("```"):
                stripped = stripped[: stripped.rfind("```")].strip()
        stripped = stripped.strip()

        if stripped.startswith("{"):
            try:
                parsed = json.loads(stripped)
                tool_name = parsed.get("name") or parsed.get("function")
                raw_args = parsed.get("arguments") or parsed.get("parameters") or {}
                if tool_name and isinstance(raw_args, dict):
                    logger.info("ollama_tool_call_content_json", tool=tool_name, args=raw_args)
                    return {"type": "tool_call", "tool": tool_name, "arguments": raw_args}
            except json.JSONDecodeError:
                pass

        # --- Path 3: Plain text final answer ---
        logger.info("ollama_final_answer", content_len=len(content))
        return {"type": "final_answer", "content": content}


# ---------------------------------------------------------------------------
# MockLLMProvider — regex-based fallback for offline/dev use
# ---------------------------------------------------------------------------

class MockLLMProvider(BaseLLMProvider):
    async def generate(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
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
                category = places[0].get("category", "places") if places else "places"
                if not places:
                    return {"type": "final_answer", "content": f"I couldn't find any {category} nearby."}
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
                location = listings[0].get("location", "") if listings else ""
                if not listings:
                    return {"type": "final_answer", "content": "No property listings found matching your budget."}
                lines = [f"**Real Estate Listings in {location}**\n"]
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

            elif tool_name == "get_satellite_info":
                loc = data.get("location", "")
                img_url = data.get("tile_url") or data.get("image_url")
                desc = data.get("description", "")
                lines = [f"**Satellite Info: {loc}**\n"]
                if desc:
                    lines.append(desc)
                if img_url:
                    lines.append(f"[View Satellite Tile]({img_url})")
                return {"type": "final_answer", "content": "\n".join(lines)}

            return {"type": "final_answer", "content": str(raw)}

        # Regex-based routing for user queries
        query = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                query = msg.get("content", "").lower()
                break

        if "weather" in query or "temperature" in query:
            match = re.search(r'in (.*)', query)
            loc = match.group(1).strip().strip('?') if match else "Pune"
            return {"type": "tool_call", "tool": "get_weather", "arguments": {"location": loc}}

        elif any(word in query for word in ["house", "buy", "rent", "property", "estate", "flat", "apartment"]):
            match = re.search(r'in ([\w\s]+?)(?: under| for| with| near|$)', query + " ")
            loc = match.group(1).strip() if match else "Kharadi"
            budget_match = re.findall(r'\b(\d+(?:\.\d+)?)(l|lakhs?|cr|crore)?\b', query.lower())
            min_b, max_b = None, None

            def parse_budget(val, suffix):
                num = float(val)
                if suffix and suffix.startswith('l'):
                    return num * 100000
                if suffix and suffix.startswith('c'):
                    return num * 10000000
                return num

            if len(budget_match) >= 2:
                min_b = parse_budget(budget_match[0][0], budget_match[0][1])
                max_b = parse_budget(budget_match[1][0], budget_match[1][1])
            elif len(budget_match) == 1:
                max_b = parse_budget(budget_match[0][0], budget_match[0][1])

            args = {"location": loc}
            if min_b:
                args["min_budget"] = min_b
            if max_b:
                args["max_budget"] = max_b
            return {"type": "tool_call", "tool": "search_real_estate", "arguments": args}

        elif "satellite" in query or "aerial" in query or "imagery" in query:
            match = re.search(r'(?:of|for|in|near) ([\w\s,]+?)(?:\?|$)', query)
            loc = match.group(1).strip() if match else "Pune"
            return {"type": "tool_call", "tool": "get_satellite_info", "arguments": {"location": loc}}

        elif "near" in query or "nearby" in query or "find" in query:
            match = re.search(r'(.*?) near (.*)', query)
            if match:
                cat = match.group(1).replace("find", "").replace("search", "").strip()
                loc = match.group(2).strip().strip('?')
            else:
                cat = "restaurant"
                loc = "Pune"
            return {"type": "tool_call", "tool": "get_nearby_places", "arguments": {"location": loc, "category": cat}}

        return {
            "type": "final_answer",
            "content": "I can help you with weather, nearby places, real estate, and satellite imagery for any location in India!"
        }


def get_llm_provider() -> BaseLLMProvider:
    provider = settings.LLM_PROVIDER.lower()
    if provider == "ollama":
        return OllamaLLMProvider()
    if provider == "mock":
        return MockLLMProvider()
    raise NotImplementedError(f"LLM provider '{provider}' is not implemented yet.")
