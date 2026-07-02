"""The classic first tool: a weather lookup.

This one is FAKE — it computes a deterministic "forecast" from the city name,
so the same city always gives the same answer (handy for testing) and you
don't need a weather API account. The LLM doesn't know it's fake: it just
sees a tool called `get_weather` and trusts the output. Remember that — an
agent is only as truthful as its tools.
"""

from langchain.tools import tool

_CONDITIONS = ["sunny", "partly cloudy", "cloudy", "light rain", "windy", "foggy"]


@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city.

    Args:
        city: Name of the city, e.g. "Rotterdam" or "Paris".
    """
    # NOTE: everything the LLM knows about this tool comes from the docstring
    # above and the argument types. Write those as if you're explaining the
    # tool to a new colleague — because that's exactly what you're doing.
    normalized = city.strip().lower()
    seed = sum(ord(c) for c in normalized)          # same city -> same number
    temperature = (seed % 30) - 2                   # somewhere between -2 and 27 °C
    condition = _CONDITIONS[seed % len(_CONDITIONS)]
    wind = (seed % 5) + 1                           # Beaufort 1-5
    return (
        f"Weather in {city.strip().title()}: {condition}, "
        f"{temperature}°C, wind force {wind}."
    )
