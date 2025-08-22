# Weather Lookup Script 🌦️

A simple Python CLI tool (`app.py`) to fetch **current or hourly weather conditions** at any location using latitude and longitude.
It uses the [Open-Meteo API](https://open-meteo.com/) for forecasts and can reverse-geocode coordinates into human-readable place names via **Open-Meteo Geocoding API** and **OpenStreetMap (OSM) Nominatim**.

---

## ✨ Features

* Get **current weather** for any location in the world.
* Query **weather at a specific time** (nearest hour).
* Automatic **reverse geocoding** of coordinates to city names:

  * Primary: Open-Meteo Geocoding
  * Fallback: OpenStreetMap Nominatim
* Human-friendly weather descriptions (WMO weather codes → text).
* Built-in input validation and error handling.
* Provides a quick OpenStreetMap link for the location.

---

## 🛠 Requirements

* Python 3.7+
* Install dependencies:

  ```bash
  pip install requests
  ```

---

## 🚀 Usage

### 1. Run with CLI arguments

```bash
python app.py <latitude> <longitude>
```

Example (Shah Alam, Malaysia):

```bash
python app.py 3.0738 101.5183
```

### 2. Run interactively

Run without arguments:

```bash
python app.py
```

You’ll be prompted to enter:

* **Latitude & Longitude** (e.g., `3.0738 101.5183`)
* **Time** (optional):

  * `now` → current weather
  * `YYYY-MM-DD HH:MM` → weather at a specific time (local)
  * blank → defaults to `now`

---

## 📋 Example Output

```
Enter latitude and longitude (e.g., 3.081 101.585): 3.0738 101.5183
Enter time to query (now for current, or YYYY-MM-DD HH:MM; leave blank for now): now

Location: Shah Alam, Selangor, MY
Coordinates: 3.07380, 101.51830
Current weather at local time 2025-08-22T15:00:
- Conditions: Partly cloudy
- Temperature: 32.1°C (feels like 35.0°C)
- Humidity: 66%    Pressure: 1007.2 hPa
- Wind: 11.2 km/h at 180°
- Cloud cover: 40%    Precipitation: 0.0 mm
- Map: https://www.openstreetmap.org/?mlat=3.073800&mlon=101.518300#map=12/3.073800/101.518300
```

---

## ⚠️ Notes

* Forecast coverage is limited to the Open-Meteo API’s available data range.
  For historical weather beyond forecasts, use [Open-Meteo Archive API](https://open-meteo.com/en/docs).
* Valid coordinate ranges:

  * Latitude: `-90` to `90`
  * Longitude: `-180` to `180`
* Please update the `USER_AGENT` string in the script with your contact info before frequent queries, as required by OSM Nominatim.

---

## 📜 License

MIT License.
You are free to use, modify, and distribute this script.
