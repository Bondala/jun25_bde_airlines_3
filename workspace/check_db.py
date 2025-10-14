import pymysql
from sqlalchemy import create_engine, inspect, text
import pandas as pd

# -------------------------------
# MySQL connection
# -------------------------------
engine = create_engine(
    "mysql+pymysql://myuser:mypassword@db:3306/mydb"
)

# -------------------------------
# Inspect the database
# -------------------------------
inspector = inspect(engine)

# List all databases (schemas)
with engine.connect() as conn:
    databases = conn.execute(text("SHOW DATABASES;")).fetchall()
    print("Databases in MySQL:")
    for db in databases:
        print(" -", db[0])

# Check if 'mydb' exists
if ("mydb",) in databases:
    print("\nDatabase 'mydb' exists!")

# List tables in 'mydb'
tables = inspector.get_table_names()
print("\nTables in 'mydb':")
for table in tables:
    print(" -", table)

# Check if 'airports' table exists
if "airports" in tables:
    print("\nTable 'airports' exists!")

    # Show first 10 rows
    df = pd.read_sql("SELECT * FROM airports LIMIT 10;", engine)
    print("\nSample data from 'airports':")
    print(df)
else:
    print("\nTable 'airports' does NOT exist!")
