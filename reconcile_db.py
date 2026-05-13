import os
import sys
from sqlalchemy import create_engine, inspect, text
from alembic.config import Config
from alembic import command
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def reconcile():
    if not DATABASE_URL:
        print("Error: DATABASE_URL not set.")
        return

    print(f"Reconciling database state for: {DATABASE_URL.split('@')[-1]}")
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    # 1. Identify existing state
    tables = inspector.get_table_names()
    print(f"Detected tables: {tables}")
    
    # 2. Check for alembic_version
    has_alembic = 'alembic_version' in tables
    current_version = None
    if has_alembic:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version_num FROM alembic_version")).fetchone()
            current_version = result[0] if result else None
    
    print(f"Current Alembic version in DB: {current_version}")

    # 3. Define expected versions
    # Initial: f3f5d907ce9f
    # Add BGM: e2ad2876ced4
    LATEST_VERSION = "e2ad2876ced4"
    INITIAL_VERSION = "f3f5d907ce9f"

    # 4. Reconciliation Logic
    if 'properties' in tables:
        columns = [c['name'] for c in inspector.get_columns('properties')]
        print(f"Columns in 'properties': {columns}")
        
        # If table exists but no alembic version, we need to stamp it
        if not current_version:
            print("Table exists but alembic_version is missing. Stamping...")
            
            # Determine if it's at initial or latest based on columns
            target_stamp = INITIAL_VERSION
            if 'bgm_id' in columns:
                target_stamp = LATEST_VERSION
            
            print(f"Stamping database to version: {target_stamp}")
            
            # Use alembic to stamp
            alembic_cfg = Config("alembic.ini")
            command.stamp(alembic_cfg, target_stamp)
            print("Stamping complete.")
            
    else:
        print("Properties table not found. Alembic will create it from scratch.")

    # 5. Run migrations to be sure
    print("Running alembic upgrade head...")
    try:
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("Migrations successfully applied/verified.")
    except Exception as e:
        print(f"Migration error: {e}")
        print("\nTIP: If you get 'column already exists', check if your models and migrations are out of sync.")

if __name__ == "__main__":
    reconcile()
