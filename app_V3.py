import sys
import requests
from datetime import datetime, timedelta

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
REVERSE_GEO_OPEN_METEO = "https://geocoding-api.open-meteo.com/v1/reverse"
REVERSE_GEO_OSM = "https://nominatim.openstreetmap.org/reverse"
USER_AGENT = "WeatherScript/1.0 (contact: your-email@example.com)"  # Please customise

# WMO weather code mapping (Open-Meteo docs)
WMO_DESC = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    56: "Light freezing drizzle", 57: "Dense freezing drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    66: "Light freezing rain", 67: "Heavy freezing rain",
    71: "Slight snowfall", 73: "Moderate snowfall", 75: "Heavy snowfall",
    77: "Snow grains",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    85: "Slight snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",
}

def parse_coords(args):
    # If provided as CLI args
    if len(args) >= 3:
        try:
            lat = float(args[1])
            lon = float(args[2])
            return lat, lon
        except ValueError:
            print("Error: Latitude and longitude must be numbers.")
            sys.exit(1)

    # Interactive input
    try:
        raw = input("Enter latitude and longitude (e.g., 3.081 101.585): ").strip()
        parts = [p.strip() for p in (raw.split(",") if "," in raw else raw.split())]
        if len(parts) != 2:
            raise ValueError("Please provide exactly two values (lat lon).")
        lat = float(parts[0])
        lon = float(parts[1])
        return lat, lon
    except Exception as e:
        print(f"Input error: {e}")
        sys.exit(1)

def validate_coords(lat, lon):
    if not (-90.0 <= lat <= 90.0):
        print("Error: Latitude must be between -90 and 90.")
        sys.exit(1)
    if not (-180.0 <= lon <= 180.0):
        print("Error: Longitude must be between -180 and 180.")
        sys.exit(1)

def prompt_time():
    raw = input("Enter time to query (now for current, or YYYY-MM-DD HH:MM; leave blank for now): ").strip()
    if raw == "" or raw.lower() == "now":
        return None  # Use current weather
    fmts = ["%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M", "%Y-%m-%d %H", "%Y-%m-%dT%H"]
    for f in fmts:
        try:
            dt = datetime.strptime(raw, f)
            return dt
        except ValueError:
            continue
    print("Could not parse time. Please use 'now' or 'YYYY-MM-DD HH:MM' (local time at the coordinates).")
    sys.exit(1)

def reverse_geocode_open_meteo(lat, lon):
    params = {"latitude": lat, "longitude": lon, "language": "en", "format": "json"}
    r = requests.get(REVERSE_GEO_OPEN_METEO, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    results = data.get("results") or []
    if not results:
        return None
    item = results[0]
    name = item.get("name")
    admin2 = item.get("admin2")
    admin1 = item.get("admin1")
    country = item.get("country")
    country_code = item.get("country_code")
    parts = [p for p in [name, admin2 or admin1, (country_code or "").upper() or country] if p]
    label = ", ".join(parts)
    return {
        "label": label or None,
        "name": name,
        "admin1": admin1,
        "admin2": admin2,
        "country": country,
        "country_code": (country_code or "").upper() if country_code else None,
        "source": "open-meteo",
    }

def reverse_geocode_osm(lat, lon):
    params = {
        "format": "jsonv2",
        "lat": lat,
        "lon": lon,
        "addressdetails": 1,
        "zoom": 12,
    }
    headers = {"User-Agent": USER_AGENT}
    r = requests.get(REVERSE_GEO_OSM, params=params, headers=headers, timeout=10)
    r.raise_for_status()
    j = r.json()
    addr = j.get("address", {}) or {}
    name = addr.get("city") or addr.get("town") or addr.get("village") or addr.get("suburb") or addr.get("hamlet")
    admin1 = addr.get("state")
    country = addr.get("country")
    country_code = (addr.get("country_code") or "").upper() if addr.get("country_code") else None
    parts = [p for p in [name, admin1, country_code or country] if p]
    label = ", ".join(parts) if parts else (j.get("display_name") or None)
    return {
        "label": label,
        "name": name,
        "admin1": admin1,
        "admin2": addr.get("county"),
        "country": country,
        "country_code": country_code,
        "source": "osm",
    }

def reverse_geocode(lat, lon):
    try:
        res = reverse_geocode_open_meteo(lat, lon)
        if res and res.get("label"):
            return res
    except requests.RequestException:
        pass
    try:
        res = reverse_geocode_osm(lat, lon)
        if res and res.get("label"):
            return res
    except requests.RequestException:
        pass
    return {"label": None, "source": None}

def get_current_weather(lat: float, lon: float):
    params = {
        "latitude": lat,
        "longitude": lon,
        "timezone": "auto",
        "current": ",".join([
            "temperature_2m",
            "apparent_temperature",
            "relative_humidity_2m",
            "precipitation",
            "weather_code",
            "cloud_cover",
            "pressure_msl",
            "wind_speed_10m",
            "wind_direction_10m",
        ]),
    }
    r = requests.get(FORECAST_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    current = data.get("current") or {}
    units = data.get("current_units") or {}
    code = current.get("weather_code")
    desc = WMO_DESC.get(code, f"Weather code {code}")
    return {
        "time": current.get("time"),
        "description": desc,
        "temperature": (current.get("temperature_2m"), units.get("temperature_2m", "°C")),
        "feels_like": (current.get("apparent_temperature"), units.get("apparent_temperature", "°C")),
        "humidity": (current.get("relative_humidity_2m"), units.get("relative_humidity_2m", "%")),
        "precipitation": (current.get("precipitation"), units.get("precipitation", "mm")),
        "cloud_cover": (current.get("cloud_cover"), units.get("cloud_cover", "%")),
        "pressure": (current.get("pressure_msl"), units.get("pressure_msl", "hPa")),
        "wind_speed": (current.get("wind_speed_10m"), units.get("wind_speed_10m", "km/h")),
        "wind_dir": (current.get("wind_direction_10m"), units.get("wind_direction_10m", "°")),
    }

def round_to_nearest_hour(dt: datetime) -> datetime:
    base = dt.replace(minute=0, second=0, microsecond=0)
    if dt.minute >= 30:
        base = base + timedelta(hours=1)
    return base

def safe_get(container, key, idx):
    arr = container.get(key)
    return arr[idx] if isinstance(arr, list) and len(arr) > idx else None

def get_weather_at_time(lat: float, lon: float, dt_local: datetime):
    target = round_to_nearest_hour(dt_local)
    params = {
        "latitude": lat,
        "longitude": lon,
        "timezone": "auto",
        "hourly": ",".join([
            "temperature_2m",
            "apparent_temperature",
            "relative_humidity_2m",
            "precipitation",
            "weather_code",
            "cloud_cover",
            "pressure_msl",
            "wind_speed_10m",
            "wind_direction_10m",
        ]),
        "start_date": target.strftime("%Y-%m-%d"),
        "end_date": target.strftime("%Y-%m-%d"),
    }
    r = requests.get(FORECAST_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    hourly = data.get("hourly") or {}
    units = data.get("hourly_units") or {}
    times = hourly.get("time") or []
    if not times:
        return None, "No hourly data returned for that date. It may be outside the available range. For older dates, use the Open-Meteo Archive API."

    target_str = target.strftime("%Y-%m-%dT%H:00")
    try:
        idx = times.index(target_str)
    except ValueError:
        return None, f"No data for {target_str} local time. Try a different time within the same day, or check forecast range."

    code = hourly.get("weather_code", [None])[idx]
    desc = WMO_DESC.get(code, f"Weather code {code}")

    result = {
        "time": times[idx],
        "description": desc,
        "temperature": (safe_get(hourly, "temperature_2m", idx), units.get("temperature_2m", "°C")),
        "feels_like": (safe_get(hourly, "apparent_temperature", idx), units.get("apparent_temperature", "°C")),
        "humidity": (safe_get(hourly, "relative_humidity_2m", idx), units.get("relative_humidity_2m", "%")),
        "precipitation": (safe_get(hourly, "precipitation", idx), units.get("precipitation", "mm")),
        "cloud_cover": (safe_get(hourly, "cloud_cover", idx), units.get("cloud_cover", "%")),
        "pressure": (safe_get(hourly, "pressure_msl", idx), units.get("pressure_msl", "hPa")),
        "wind_speed": (safe_get(hourly, "wind_speed_10m", idx), units.get("wind_speed_10m", "km/h")),
        "wind_dir": (safe_get(hourly, "wind_direction_10m", idx), units.get("wind_direction_10m", "°")),
    }
    return result, None

def main():
    lat, lon = parse_coords(sys.argv)
    validate_coords(lat, lon)

    # Reverse geocode
    location = reverse_geocode(lat, lon)
    label = location.get("label") or f"{lat:.5f}, {lon:.5f}"

    # Ask for time
    dt_local = prompt_time()

    try:
        if dt_local is None:
            wx = get_current_weather(lat, lon)
            print(f"Location: {label}")
            print(f"Coordinates: {lat:.5f}, {lon:.5f}")
            print(f"Current weather at local time {wx['time']}:")
        else:
            wx, err = get_weather_at_time(lat, lon, dt_local)
            print(f"Location: {label}")
            print(f"Coordinates: {lat:.5f}, {lon:.5f}")
            if err:
                print(err)
                sys.exit(1)
            print(f"Weather at local time {wx['time']} (nearest hour to your input):")

        print(f"- Conditions: {wx['description']}")
        print(f"- Temperature: {wx['temperature'][0]}{wx['temperature'][1]} "
              f"(feels like {wx['feels_like'][0]}{wx['feels_like'][1]})")
        print(f"- Humidity: {wx['humidity'][0]}{wx['humidity'][1]}    "
              f"Pressure: {wx['pressure'][0]} {wx['pressure'][1]}")
        print(f"- Wind: {wx['wind_speed'][0]} {wx['wind_speed'][1]} "
              f"at {wx['wind_dir'][0]}{wx['wind_dir'][1]}")
        print(f"- Cloud cover: {wx['cloud_cover'][0]}{wx['cloud_cover'][1]}    "
              f"Precipitation: {wx['precipitation'][0]} {wx['precipitation'][1]}")
        print(f"- Map: https://www.openstreetmap.org/?mlat={lat:.6f}&mlon={lon:.6f}#map=12/{lat:.6f}/{lon:.6f}")
    except requests.HTTPError as e:
        status = e.response.status_code if e.response is not None else "HTTP error"
        print(f"HTTP error: {status}")
        sys.exit(1)
    except requests.RequestException as e:
        print(f"Network error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
