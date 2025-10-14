from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
from sqlalchemy import create_engine, text
import math
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global variables
engine = None
df_airports = None

# -------------------------------
# Database connection and data loading
# -------------------------------
def init_app():
    global engine, df_airports
    
    # Initialize database connection
    engine = create_db_connection()
    if engine is None:
        logger.error("Failed to establish database connection")
        return False
    
    # Load airports data
    try:
        df_airports = load_airports_data()
        logger.info(f"Successfully loaded {len(df_airports)} airports")
        return True
    except Exception as e:
        logger.error(f"Failed to load airports data: {e}")
        return False

def create_db_connection():
    # Retry logic for database connection
    max_retries = 10
    retry_delay = 5
    
    for i in range(max_retries):
        try:
            engine = create_engine(
                "mysql+pymysql://myuser:mypassword@db:3306/mydb",
                pool_pre_ping=True,
                pool_recycle=3600
            )
            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection successful")
            return engine
        except Exception as e:
            logger.warning(f"Database connection failed (attempt {i+1}/{max_retries}): {e}")
            if i < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Could not connect to database after multiple attempts")
                return None

def load_airports_data():
    if engine is None:
        raise Exception("Database connection not available")
    
    max_retries = 20
    retry_delay = 5
    
    for i in range(max_retries):
        try:
            with engine.connect() as conn:
                # Check if airports table exists and has data
                result = conn.execute(text("SELECT COUNT(*) FROM airports"))
                count = result.scalar()
                if count > 0:
                    logger.info(f"Found {count} airports in database")
                    return pd.read_sql("SELECT * FROM airports", conn)
                else:
                    logger.info("Airports table is empty, waiting for data...")
                    time.sleep(retry_delay)
        except Exception as e:
            logger.warning(f"Error checking airports data (attempt {i+1}/{max_retries}): {e}")
            time.sleep(retry_delay)
    
    raise Exception("Could not load airports data after multiple attempts")

# Initialize the application
app_initialized = init_app()

# -------------------------------
# Haversine formula
# -------------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))  # <-- fixed here
    return R * c
# -------------------------------
# Serve HTML template
# -------------------------------
@app.route("/")
def index():
    return render_template("index.html")

# -------------------------------
# API endpoint
# -------------------------------
@app.route("/closest_airport", methods=["POST"])
def closest_airport():
    # Check if app is initialized
    if not app_initialized or df_airports is None:
        return jsonify({"error": "Application is still initializing. Please try again in a few moments."}), 503
    
    data = request.get_json()
    if not data or "latitude" not in data or "longitude" not in data:
        return jsonify({"error": "Please provide latitude and longitude"}), 400

    try:
        user_lat = float(data["latitude"])
        user_lon = float(data["longitude"])
    except ValueError:
        return jsonify({"error": "Invalid latitude or longitude values"}), 400

    # Validate coordinates
    if not (-90 <= user_lat <= 90) or not (-180 <= user_lon <= 180):
        return jsonify({"error": "Coordinates out of valid range"}), 400

    # Calculate distances
    df_airports["DistanceKm"] = df_airports.apply(
        lambda row: haversine(user_lat, user_lon, row["Latitude"], row["Longitude"]), axis=1
    )

    closest = df_airports.loc[df_airports["DistanceKm"].idxmin()]

    return jsonify({
        "AirportCode": closest["AirportCode"],
        "CityCode": closest["CityCode"],
        "CountryName": closest["CountryName"],
        "Latitude": closest["Latitude"],
        "Longitude": closest["Longitude"],
        "DistanceKm": round(closest["DistanceKm"], 2)
    })

import subprocess
@app.route("/run_data_import", methods=["POST"])
def run_data_import():
    try:
        # Run the script using subprocess
        result = subprocess.run(
            ["python3", "airlines_api_call.py"],
            capture_output=True,
            text=True,
            check=True
        )
        return jsonify({
            "status": "success",
            "output": result.stdout
        }), 200

    except subprocess.CalledProcessError as e:
        return jsonify({
            "status": "error",
            "message": "Script execution failed",
            "stderr": e.stderr
        }), 500


# Health check endpoint
@app.route("/health")
def health():
    try:
        if engine:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            db_status = "connected"
        else:
            db_status = "disconnected"
        
        airports_count = len(df_airports) if df_airports is not None else 0
        app_status = "ready" if app_initialized else "initializing"
        
        return jsonify({
            "status": app_status,
            "database": db_status,
            "airports_count": airports_count
        })
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

# Endpoint to check if airports data is loaded
@app.route("/status")
def status():
    if app_initialized and df_airports is not None and len(df_airports) > 0:
        return jsonify({"status": "ready", "airports_count": len(df_airports)})
    else:
        return jsonify({"status": "initializing", "message": "Application is still initializing"}), 503

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)