import os
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("Error: DATABASE_URL not found in .env")
    exit(1)

print(f"Inspecting database: {DATABASE_URL.split('@')[-1]}")

try:
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)

    # 1. List Schemas
    schemas = inspector.get_schema_names()
    print(f"Schemas found: {schemas}")

    for schema in schemas:
        if schema in ['information_schema', 'pg_catalog']:
            continue
        print(f"\n--- Schema: {schema} ---")
        # 1. List Tables
        tables = inspector.get_table_names(schema=schema)
        print(f"Tables found: {tables}")

        # 2. Check alembic_version
        if 'alembic_version' in tables:
            with engine.connect() as conn:
                from sqlalchemy import text
                result = conn.execute(text(f'SELECT version_num FROM "{schema}".alembic_version')).fetchone()
                print(f"Current Alembic Version: {result[0] if result else 'Empty'}")
        else:
            print("alembic_version table NOT found.")

        # 3. Inspect 'properties' table if it exists
        if 'properties' in tables:
            print(f"Columns in '{schema}.properties' table:")
            columns = inspector.get_columns('properties', schema=schema)
            for col in columns:
                print(f" - {col['name']} ({col['type']})")
        else:
            print(f"'properties' table NOT found in {schema}.")

except Exception as e:
    print(f"Error during inspection: {e}")
