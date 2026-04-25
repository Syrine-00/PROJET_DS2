"""
api_tool — fetches external data with allow-list enforcement,
explicit timeouts, and bounded retries via tenacity.
"""

import requests
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError

from security.allow_list import is_host_allowed
from tools.schemas import FetchWeatherInput, FetchWeatherOutput, FetchApiOutput
from tools.read_csv_tool import ToolError

# ── Weather fetch ─────────────────────────────────────────────────────────────

WEATHER_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude={lat}&longitude={lon}&current_weather=true"
)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
def _get_with_retry(url: str, timeout: int) -> requests.Response:
    resp = requests.get(url, timeout=timeout)
    if resp.status_code == 429:
        raise IOError("HTTP 429: rate limited")
    if resp.status_code != 200:
        raise IOError(f"HTTP {resp.status_code}: request failed")
    return resp


def fetch_weather_data(
    latitude: float = 36.8,
    longitude: float = 10.1,
    timeout: int = 10,
) -> dict:
    """
    Fetch current weather for a Tunisia coordinate.
    - Allow-list enforced
    - Explicit timeout
    - Bounded retry (3 attempts, exponential backoff)
    """
    inp = FetchWeatherInput(latitude=latitude, longitude=longitude, timeout=timeout)
    url = WEATHER_URL.format(lat=inp.latitude, lon=inp.longitude)

    if not is_host_allowed(url):
        raise ToolError(f"SAFETY_BLOCK: host not in allow-list for URL: {url}")

    try:
        resp = _get_with_retry(url, inp.timeout)
    except (RetryError, IOError) as e:
        raise ToolError(f"API_FAILURE: {e}")

    raw = resp.json()
    cw = raw.get("current_weather", {})

    temp = cw.get("temperature", 0.0)
    output = FetchWeatherOutput(
        temperature=temp,
        windspeed=cw.get("windspeed", 0.0),
        tourism_impact="high" if temp > 25 else "medium",
    )
    return output.model_dump()


# ── Mock API data (Scenario 2 fallback / simulation) ─────────────────────────

def fetch_api_data() -> dict:
    """
    Returns mock tourism indicator data for Tunisia.
    Simulates a real API response for Scenario 2.
    """
    output = FetchApiOutput(
        top_regions={"Tunis": 120000.0, "Sousse": 95000.0, "Djerba": 87000.0},
        total_revenue=302000.0,
        average_occupancy_rate=78.0,
    )
    return output.model_dump()
