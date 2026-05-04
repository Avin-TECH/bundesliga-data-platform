"""
Database connection utilities.
Provides a simple way to connect to Postgres using credentials from .env.
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """Return a connection to the Postgres database."""
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        database=os.getenv("POSTGRES_DB"),
    )


def test_connection():
    """Verify we can connect and Postgres responds."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return version


if __name__ == "__main__":
    print("Attempting to connect to Postgres...")
    try:
        version = test_connection()
        print(f"✅ Connection successful!")
        print(f"Postgres version: {version}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")