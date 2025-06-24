import pandas as pd
import requests
import time

# API Key 
API_KEY = "AIzaSyDenuTITy06MWYH2BnzFnwEaW91cHjVuSw"

# Datei laden
df = pd.read_csv("unique_tripadvisor_places_Trialbatch.csv")

# Neue Spalten vorbereiten
df["latitude"] = None
df["longitude"] = None
df["type"] = None
df["price level"] = None
df["avg. google rating"] = None
df["operational status"] = None  # Neue Spalte für den Status

# Basis-URL der Google Places API
endpoint_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"

for index, row in df.iterrows():
    query = f"{row['Reviewed Location Name']}, {row['City']}, {row['Country']}"
    params = {
        "input": query,
        "inputtype": "textquery",
        "fields": "place_id,geometry,types,rating,price_level,business_status",
        "key": API_KEY
    }

    response = requests.get(endpoint_url, params=params)
    result = response.json()

    if result.get("candidates"):
        candidate = result["candidates"][0]
        location = candidate["geometry"]["location"]
        df.at[index, "latitude"] = location["lat"]
        df.at[index, "longitude"] = location["lng"]

        # hole type
        types = candidate.get("types")
        if types:
            df.at[index, "type"] = types[0]  # nur erster Typ

        # hole rating
        rating = candidate.get("rating")
        if rating is not None:
            df.at[index, "avg. google rating"] = rating

        # hole price level
        price_level = candidate.get("price_level")
        if price_level is not None:
            df.at[index, "price level"] = price_level

        # hole operational status
        status = candidate.get("business_status")
        if status:
            df.at[index, "operational status"] = status

    else:
        print(f"Kein Treffer für: {query}")

    time.sleep(0.2)  # Rate Limiting

# Ergebnis speichern
df.to_csv("places_with_full_info.csv", index=False)
print("Datei gespeichert: places_with_full_info.csv")
