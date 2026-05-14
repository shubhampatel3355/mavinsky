from sqlalchemy import text
from database import engine

def add_documents_column():
    try:
        with engine.connect() as conn:
            print("Connecting to database...")
            # Check if column exists first
            result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='properties' AND column_name='documents'"))
            if not result.fetchone():
                print("Adding 'documents' column to 'properties' table...")
                conn.execute(text("ALTER TABLE properties ADD COLUMN documents JSONB DEFAULT '[]'::jsonb"))
                conn.commit()
                print("Column 'documents' added successfully!")
            else:
                print("Column 'documents' already exists.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    add_documents_column()
