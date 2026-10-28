import asyncio
import os

from dotenv import load_dotenv
from ddgs import DDGS
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Load OPENAI_API_KEY from the .env file
load_dotenv()


def search_weather_news(city: str, max_results: int = 5) -> str:
    """Search the web for the latest weather news and current weather conditions for a city.

    Args:
        city: Name of the city to search weather news for, e.g. "Chennai".
        max_results: Maximum number of results to return per search.

    Returns:
        Recent weather news headlines and current-weather snippets with links.
    """
    ddgs = DDGS()
    lines = []

    try:
        news = ddgs.news(f"{city} weather", max_results=max_results)
        for r in news or []:
            lines.append(
                f"- [NEWS {r.get('date', '')}] {r.get('title', '')}: "
                f"{r.get('body', '')} ({r.get('url', '')})"
            )
    except Exception as e:
        lines.append(f"News search failed: {e}")

    try:
        web = ddgs.text(f"{city} weather today temperature", max_results=max_results)
        for r in web or []:
            lines.append(
                f"- [WEB] {r.get('title', '')}: {r.get('body', '')} ({r.get('href', '')})"
            )
    except Exception as e:
        lines.append(f"Web search failed: {e}")

    return "\n".join(lines) if lines else f"No weather information found for {city}."


async def main() -> None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not found. Add it to your .env file.")

    city = input("Enter a city name: ").strip()
    if not city:
        print("City name cannot be empty.")
        return

    model_client = OpenAIChatCompletionClient(
        model="gpt-4o-mini",
        api_key=api_key,
    )

    agent = AssistantAgent(
        name="weather_news_agent",
        model_client=model_client,
        tools=[search_weather_news],
        reflect_on_tool_use=True,
        system_message=(
            "You are a weather news assistant. "
            "Always use the search_weather_news tool to get the latest information for the city. "
            "Using only the search results, reply in exactly 3 short lines: "
            "line 1 = current conditions (temperature, sky, humidity if available), "
            "line 2 = the latest weather news or alert, "
            "line 3 = the short-term outlook. "
            "Use specific facts and numbers from the results. "
            "Do not tell the user to check websites. No heading, no bullets, no extra text."
        ),
    )

    try:
        await Console(
            agent.run_stream(task=f"Give me the latest weather news for {city}.")
        )
    finally:
        await model_client.close()


if __name__ == "__main__":
    asyncio.run(main())