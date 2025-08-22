# Weather Lookup Script 🌦️

A simple Python CLI tool to fetch **current or hourly weather conditions** at any location using latitude and longitude.
It uses the [Open-Meteo API](https://open-meteo.com/) for forecasts and can reverse-geocode coordinates into human-readable place names via **Open-Meteo Geocoding API** and **OpenStreetMap (OSM) Nominatim**.

---

## ✨ Features

* Fetch **current weather** conditions for given coordinates.
* Query **past or future weather** (nearest hour) by entering a datetime.
* Automatic **reverse geocoding** of coordinates into location labels:

  * Primary: Open-Meteo Geocoding
  * Fallback: OpenStreetMap Nominatim
* Friendly weather descriptions mapped from **WMO weather codes**.
* Handles input errors, invalid coordinates, and network failures gracefully.
* Outputs OpenStreetMap link for quick location visualization.

---

## 🛠 Requirements

* Python 3.7+
* Dependencies:

  ```bash
  pip install requests
  ```

---

## 🚀 Usage

### 1. Run with CLI arguments

```bash
python weather.py <latitude> <longitude>
```

Example:

```bash
python weather.py 11.2879 95.7300
```

### 2. Run interactively

Simply run without arguments:

```bash
python weather.py
```

You will be prompted to enter:

* **Latitude & Longitude** (e.g., `3.081 101.585`)
* **Time** (optional):

  * `now` → current weather
  * `YYYY-MM-DD HH:MM` → weather at a specific time (nearest hour, local to that location)
  * blank → same as `now`

---

## 📋 Example Output

```
Enter latitude and longitude (e.g., 3.081 101.585): 11.2879 95.7300
Enter time to query (now for current, or YYYY-MM-DD HH:MM; leave blank for now): now

Location: Port Blair, Andaman and Nicobar Islands, IN
Coordinates: 11.28790, 95.73000
Current weather at local time 2025-08-22T12:45:
- Conditions: Overcast
- Temperature: 27.8°C (feels like 29.9°C)
- Humidity: 81%    Pressure: 1008.9 hPa
- Wind: 9.4 km/h at 210°
- Cloud cover: 100%    Precipitation: 0.0 mm
- Map: https://www.openstreetmap.org/?mlat=11.287900&mlon=95.730000#map=12/11.287900/95.730000
```

---

## ⚠️ Notes

* The script queries **Open-Meteo Forecast API** for current/forecasted data.
  For historical weather beyond forecast availability, use [Open-Meteo Archive API](https://open-meteo.com/en/docs).
* Coordinates must be valid:

  * Latitude: `-90` to `90`
  * Longitude: `-180` to `180`
* Please update the `USER_AGENT` string in the script with your contact information before heavy use, as OSM Nominatim requires this.

---

## 📜 License

MIT License.
You are free to use, modify, and distribute this script.
