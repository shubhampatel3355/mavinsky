import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv(override=True)
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    print("Listing all property IDs in the current database...")
    result = conn.execute(text("SELECT id, title FROM properties LIMIT 10")).fetchall()
    for row in result:
        print(f"ID: {row[0]}, Title: {row[1]}")
