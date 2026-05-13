import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SHOW search_path")).fetchone()
        print(f"Current search_path: {result[0]}")
        
        result = conn.execute(text("SELECT current_user, current_database()")).fetchone()
        print(f"Current user: {result[0]}, Database: {result[1]}")
except Exception as e:
    print(f"Error: {e}")
