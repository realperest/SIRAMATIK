
import sys
import os

# Ensure backend directory is in path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db

def drop_public_siralar():
    try:
        print("Dropping public.siralar VIEW...")
        db.execute_query("DROP VIEW IF EXISTS public.siralar CASCADE;")
        print("Dropped VIEW public.siralar.")
    except Exception as e:
        print(f"Error dropping VIEW: {e}")

    try:
        print("Dropping public.siralar TABLE...")
        db.execute_query("DROP TABLE IF EXISTS public.siralar CASCADE;")
        print("Dropped TABLE public.siralar.")
    except Exception as e:
        print(f"Error dropping TABLE: {e}")

if __name__ == "__main__":
    drop_public_siralar()
