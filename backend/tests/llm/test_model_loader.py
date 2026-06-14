import pytest
from app.llm.model_loader import MockLLMProvider

@pytest.mark.asyncio
async def test_mock_llm_weather():
    provider = MockLLMProvider()
    res = await provider.generate([{"role": "user", "content": "What is the weather in Kharadi"}])
    assert res["type"] == "tool_call"
    assert res["tool"] == "get_weather"
    assert res["arguments"]["location"] == "kharadi"

@pytest.mark.asyncio
async def test_mock_llm_real_estate():
    provider = MockLLMProvider()
    res = await provider.generate([{"role": "user", "content": "I want to buy a house in Wagholi budget 20"}])
    assert res["type"] == "tool_call"
    assert res["tool"] == "search_real_estate"
    assert "wagholi" in res["arguments"]["location"]
    
@pytest.mark.asyncio
async def test_mock_llm_final_answer():
    provider = MockLLMProvider()
    res = await provider.generate([{"role": "user", "content": "Hello"}])
    assert res["type"] == "final_answer"
    
@pytest.mark.asyncio
async def test_mock_llm_tool_result():
    provider = MockLLMProvider()
    res = await provider.generate([
        {"role": "user", "content": "weather in Pune"},
        {"role": "tool", "content": "{\"temp\": 30}"}
    ])
    assert res["type"] == "final_answer"
    assert "30" in res["content"]
