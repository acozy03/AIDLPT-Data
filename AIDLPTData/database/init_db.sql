import psycopg2

# Connect to PostgreSQL
conn = psycopg2.connect("dbname=ai_project user=admin password=secret")
cursor = conn.cursor()

# Create table
cursor.execute("""
    CREATE TABLE text_data (
        id SERIAL PRIMARY KEY,
        language TEXT,
        original_text TEXT,
        cleaned_text TEXT
    )
""")
conn.commit()
