import os
import psycopg2
from psycopg2 import sql
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

db_url = os.environ.get("DATABASE_URL")
parsed_url = urlparse(db_url)

db_name = parsed_url.path.lstrip("/")
user = parsed_url.username
password = parsed_url.password
host = parsed_url.hostname
port = parsed_url.port or 5432

# Connect to 'postgres' database
conn = psycopg2.connect(
    dbname="postgres",
    user=user,
    password=password,
    host=host,
    port=port
)
conn.autocommit = True  
cur = conn.cursor()

# Check if database exists
cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", [db_name])
exists = cur.fetchone()

if exists:
    print(f"Database '{db_name}' already exists.")
else:
    cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
    print(f"Database '{db_name}' created successfully!")

cur.close()
conn.close()
