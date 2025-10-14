import requests
import pandas as pd
import time
import pycountry
from sqlalchemy import create_engine, inspect, text


import sys
# Redirect all print output to a file
#sys.stdout = open("output.txt", "w")


# -------------------------------
# MySQL connection via SQLAlchemy
# -------------------------------
engine = create_engine(
    "mysql+pymysql://myuser:mypassword@db:3306/mydb"
)

# -------------------------------
# Lufthansa API credentials
# -------------------------------
auth_url = "https://api.lufthansa.com/v1/oauth/token"
client_id = "q6u5anwcj9emxxdbrunj9ywsx"
client_secret = "Dm4YJctw2X"

# Get access token
data = {
    "client_id": client_id,
    "client_secret": client_secret,
    "grant_type": "client_credentials"
}

response = requests.post(auth_url, data=data)
response.raise_for_status()
json_response = response.json()

print("Auth response:", response.status_code)
print(json_response)

access_token = json_response["access_token"]

# -------------------------------
# Retrieve airports
# -------------------------------
url = "https://api.lufthansa.com/v1/references/airports"
headers = {"Authorization": f"Bearer {access_token}"}

all_airports = []
offset = 0
limit = 100

while True:
    params = {"limit": limit, "offset": offset}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    airports = data.get("AirportResource", {}).get("Airports", {}).get("Airport", [])
    if not airports:
        print(f"Reached end of results at offset {offset}.")
        break

    all_airports.extend(airports)

    # Stop if we got fewer than requested, means no more data
    if len(airports) < limit:
        break

    offset += limit
    time.sleep(0.5)

# -------------------------------
# Flatten data into DataFrame
# -------------------------------
records = []
for airport in all_airports:
    airport_code = airport.get("AirportCode")
    city_code = airport.get("CityCode")
    country_code = airport.get("CountryCode")
    coord = airport.get("Position", {}).get("Coordinate", {})
    lat = coord.get("Latitude")
    lon = coord.get("Longitude")

    records.append({
        "AirportCode": airport_code,
        "CityCode": city_code,
        "CountryCode": country_code,
        "Latitude": lat,
        "Longitude": lon
    })

df = pd.DataFrame(records)

# -------------------------------
# Map country codes to names
# -------------------------------
def get_country_name(code):
    try:
        country = pycountry.countries.get(alpha_2=code)
        return country.name if country else None
    except Exception:
        return None

print("print second head")
print(df.head(5))

df["CountryName"] = df["CountryCode"].apply(get_country_name)
print("print second head")
print(df.head(5))



# Check if the table is already present, if so read, and update it
# engine = create_engine("mysql+pymysql://user:password@host/dbname")
inspector = inspect(engine)
if "airports" in inspector.get_table_names():
    df_copy = df
    df_table = pd.read_sql("airports", con=engine)
    
    # AirportCodes in API but not in table
    missing_in_df_table = df_copy[~df_copy["AirportCode"].isin(df_table["AirportCode"])]
    
    # AirportCodes in table but not in API
    missing_in_df_API = df_table[~df_table["AirportCode"].isin(df_copy["AirportCode"])]
    
    print("AirportCodes in df_copy but not in df_table:")
    print(missing_in_df_table)

    print("\nAirportCodes in df_table but not in df_copy:")
    print(missing_in_df_API)

    with engine.connect() as conn:
        # Check if the column already exists
        result = conn.execute(text("SHOW COLUMNS FROM airports LIKE 'CountryCode';"))
        column_exists = result.fetchone() is not None

        if not column_exists:
            # Add the column (position doesn't matter)
            conn.execute(text("ALTER TABLE airports ADD COLUMN CountryCode VARCHAR(10);"))
            conn.commit()
            
    # add missing ones from the API to table
    if (missing_in_df_table.shape[0]>0):
        missing_in_df_table.to_sql(
            name='airports',
            con=engine,
            if_exists='append',  # Append to existing table
            index=False           # Don't write DataFrame index as a column
        )
        
    # delete the ones which are not in the API, but in the table
    with engine.begin() as conn:
        for _, row in missing_in_df_API.iterrows():
            conn.execute(
                text("DELETE FROM airports WHERE AirportCode = :code"),
                {"code": row["AirportCode"]}
            )
                     
    df_table_after = pd.read_sql("airports", con=engine)
    print("Print after:")
    print("Size of table after deleting difference:")
    print("Size of table after deleting difference:")
    print(df_table_after.shape)
    error_check_1 = df_copy[~df_copy["AirportCode"].isin(df_table_after["AirportCode"])]
    error_check_2 = df_table_after[~df_table_after["AirportCode"].isin(df_copy["AirportCode"])]
    print("These must be 0:")
    print(error_check_1.shape)
    print(error_check_2.shape)
    
else: 
    # just create it new and fill it completely with all the airports from the API
    # -------------------------------
    # Save to MySQL
    # -------------------------------
    with engine.begin() as conn:
        df.to_sql("airports", conn, if_exists="replace", index=False)

# -------------------------------
# Verify data
# -------------------------------
with engine.begin() as conn:
    results_df = pd.read_sql("SELECT * FROM airports LIMIT 5", conn)
print("print verified results")
print(results_df)
