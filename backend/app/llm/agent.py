import structlog
import os
from app.llm.model_loader import BaseLLMProvider
from app.llm.tool_schema import TOOLS
from app.services.geocoding import GeocodingService
from app.services.weather import WeatherService
from app.services.places import PlacesService
from app.services.satellite import SatelliteService
from app.services.realestate import RealEstateService
from app.services.rag import RAGService
from app.schemas.response import GeocodingResult
from app.schemas.query import QueryResponse
from app.utils.exceptions import ExternalAPIError, LocationNotFoundError

logger = structlog.get_logger()

class GeoAIAgent:
    def __init__(
        self,
        llm_provider: BaseLLMProvider,
        geocoding_service: GeocodingService,
        weather_service: WeatherService,
        places_service: PlacesService,
        satellite_service: SatelliteService,
        realestate_service: RealEstateService,
        rag_service: RAGService
    ):
        self.llm = llm_provider
        self.geocode = geocoding_service
        self.weather = weather_service
        self.places = places_service
        self.satellite = satellite_service
        self.realestate = realestate_service
        self.rag = rag_service
        
        prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "system_prompt.txt")
        try:
            with open(prompt_path, "r") as f:
                self.system_prompt = f.read()
        except FileNotFoundError:
            self.system_prompt = "You are GeoAI-Core."

    async def process_query(self, query: str, session_id: str | None = None) -> QueryResponse:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": query}
        ]
        tools_used = []
        
        result = await self.llm.generate(messages, tools=TOOLS)
        
        if result.get("type") == "tool_call":
            tool_name = result.get("tool")
            args = result.get("arguments", {})
            tools_used.append(tool_name)
            
            try:
                tool_result_content = ""
                
                if tool_name == "get_weather":
                    loc = args.get("location")
                    geo = await self.geocode.geocode(loc)
                    weather_data = await self.weather.get_current_weather(geo.latitude, geo.longitude, geo.display_name)
                    tool_result_content = weather_data.model_dump_json()
                    
                elif tool_name == "get_nearby_places":
                    loc = args.get("location")
                    cat = args.get("category")
                    geo = await self.geocode.geocode(loc)
                    places_data = await self.places.get_nearby_places(geo.latitude, geo.longitude, cat)
                    tool_result_content = places_data.model_dump_json()
                    
                elif tool_name == "get_satellite_info":
                    loc = args.get("location")
                    geo = await self.geocode.geocode(loc)
                    sat_data = await self.satellite.get_satellite_info(geo.latitude, geo.longitude, geo.display_name)
                    tool_result_content = sat_data.model_dump_json()
                    
                elif tool_name == "search_real_estate":
                    loc = args.get("location")
                    min_b = args.get("min_budget")
                    max_b = args.get("max_budget")
                    re_data = await self.realestate.search_listings(loc, min_b, max_b)
                    tool_result_content = re_data.model_dump_json()
                    
                elif tool_name == "geocode_location":
                    loc = args.get("location")
                    geo = await self.geocode.geocode(loc)
                    tool_result_content = geo.model_dump_json()
                    
                else:
                    tool_result_content = f"Unknown tool: {tool_name}"
                    
                # Call LLM again with tool result
                messages.append({"role": "tool", "name": tool_name, "content": tool_result_content})
                final_result = await self.llm.generate(messages, tools=TOOLS)
                
                return QueryResponse(
                    answer=final_result.get("content", ""),
                    tools_used=tools_used
                )
                
            except LocationNotFoundError:
                return QueryResponse(answer="Sorry, I couldn't find information for that location.", tools_used=tools_used)
            except ExternalAPIError as e:
                return QueryResponse(answer=f"Sorry, I encountered an error while fetching data: {e}", tools_used=tools_used)
            except Exception as e:
                logger.error("agent_error", error=str(e))
                return QueryResponse(answer="An unexpected error occurred while processing your request.", tools_used=tools_used)
        
        elif result.get("type") == "final_answer":
            return QueryResponse(
                answer=result.get("content", ""),
                tools_used=tools_used
            )
            
        return QueryResponse(answer="No answer could be generated.", tools_used=tools_used)
