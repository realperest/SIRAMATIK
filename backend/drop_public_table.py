
import sys
import os

# Ensure backend directory is in path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db

def drop_public_siralar():
    try:
        print("Dropping public.siralar table...")
        db.execute_query("DROP TABLE IF EXISTS public.siralar CASCADE;")
        print("Successfully dropped public.siralar (if it existed).")
    except Exception as e:
        print(f"Error dropping table: {e}")

if __name__ == "__main__":
    drop_public_siralar()
