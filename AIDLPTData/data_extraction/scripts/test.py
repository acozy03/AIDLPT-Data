import psycopg2

try:
    # Connect to your PostgreSQL database
    conn = psycopg2.connect(
        dbname="ai_project",
        user="postgres",
        password="SD_Is_Cool",
        host="localhost",  # Use appropriate host (e.g., localhost or IP)
        port="5432"        # Default port for PostgreSQL
    )
    print("Database connection successful!")
    conn.close()
except psycopg2.Error as e:
    print("Error connecting to the database:", e)
