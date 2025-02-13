from flask import Flask, request, jsonify
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

app = Flask(__name__)

@app.route('/get_text', methods=['GET'])
def get_text():
    lang = request.args.get("language", "en")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM text_data WHERE language = %s LIMIT 10", (lang,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)