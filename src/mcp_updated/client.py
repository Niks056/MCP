import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq

# Load environment variables from .env (in parent or root directory)
load_dotenv(Path(__file__).parent.parent / ".env")
load_dotenv(Path(__file__).parent / ".env")

MATH_SERVER_PATH = str(Path(__file__).parent / "mathserver.py")

async def main():
    client = MultiServerMCPClient(
        {
            "math": {
                "command": sys.executable,
                "args": [MATH_SERVER_PATH],
                "transport": "stdio",
            },
            # Weather server runs on port 8000 (start with: python src/mcp_updated/weather.py)
            "weather": {
                "url": "http://127.0.0.1:8000/mcp",
                "transport": "streamable-http",
            },
        }
    )

    tools = await client.get_tools()
    model = ChatGroq(model="openai/gpt-oss-120b")
    agent = create_react_agent(model, tools)

    math_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "what's (3+5) *12 ?"}]}
    )
    print("Math Response:", math_response["messages"][-1].content)

    weather_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "What is the weather in California"}]}
    )
    print("Weather Response:", weather_response["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())






    