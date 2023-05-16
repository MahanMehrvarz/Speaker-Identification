from flask import Flask, request, jsonify
import threading
import queue
import sprec
import record
import json

import sqlite3
from datetime import datetime

# Database setup
def create_db():
    conn = sqlite3.connect('speakers.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS speakers
                 (id TEXT PRIMARY KEY, weight INTEGER, last_recognized TEXT, image TEXT)''')
    conn.commit()
    conn.close()

create_db()

def update_speaker_record(speaker_id):
    conn = sqlite3.connect('speakers.db')
    c = conn.cursor()

    # Check if the speaker already exists in the database
    c.execute("SELECT * FROM speakers WHERE id=?", (speaker_id,))
    speaker = c.fetchone()

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    image_path = f"./Data/{speaker_id}/{speaker_id}.jpg"

    if speaker:
        # Update the existing speaker's weight and last_recognized timestamp
        c.execute("UPDATE speakers SET weight=?, last_recognized=?, image=? WHERE id=?",
                  (speaker[1] + 1, current_time, image_path, speaker_id))
    else:
        # Insert a new speaker record
        c.execute("INSERT INTO speakers (id, weight, last_recognized, image) VALUES (?, ?, ?, ?)",
                  (speaker_id, 1, current_time, image_path))

    conn.commit()
    conn.close()
    # Update the JSON mirror of the database
    json_data = db_to_json()
    save_json_data(json_data)

    
#converting the db to json
def db_to_json():
    conn = sqlite3.connect('speakers.db')
    conn.row_factory = sqlite3.Row  # Enable fetching rows as dictionaries
    c = conn.cursor()

    c.execute("SELECT * FROM speakers")
    rows = c.fetchall()

    # Convert rows to dictionaries and then to a JSON string
    json_data = json.dumps([dict(row) for row in rows], indent=2)

    conn.close()
    return json_data

#putin the json in a file
def save_json_data(json_data, filename="speakers.json"):
    with open(filename, "w") as json_file:
        json_file.write(json_data)


app = Flask(__name__)
rec = sprec.Recognizer()
audio_queue = queue.Queue()

@app.route('/recognize', methods=['POST'])
def recognize():
    audio_path = request.form['audio_path']
    audio_queue.put(audio_path)
    return jsonify({"status": "success"})

def recognize_speaker(q, recognizer):
    while True:
        if not q.empty():
            audio_path = q.get()
            print("Starting recognition:")
            speaker = recognizer.find_speaker(audio_path)
            if speaker:
                print(f"Speaker: {speaker}")
                update_speaker_record(speaker)
            else:
                print("Speaker not recognized")
            print("Recognition done\n")

if __name__ == '__main__':
    recognition_thread = threading.Thread(target=recognize_speaker, args=(audio_queue, rec))
    recognition_thread.start()

    # Run the Flask app
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
