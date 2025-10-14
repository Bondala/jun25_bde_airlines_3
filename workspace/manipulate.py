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


# Check if the table is already present, if so read, and update it
# engine = create_engine("mysql+pymysql://user:password@host/dbname")
inspector = inspect(engine)
if "airports" in inspector.get_table_names():
    
    df_table = pd.read_sql("airports", con=engine)
    print("Size of table before delete:")
    print(df_table.shape)
    with engine.begin() as conn:
        conn.execute(
            text("""
                DELETE FROM airports 
                WHERE AirportCode IN (
                    SELECT code FROM (
                        SELECT AirportCode AS code 
                        FROM airports 
                        ORDER BY AirportCode 
                        LIMIT 1
                    ) AS temp
                )
            """)
        )

    print("Size of table after delete:")
    df_table_after = pd.read_sql("airports", con=engine)
    print(df_table_after.shape)
    
