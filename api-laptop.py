from flask import Flask, request, jsonify
import threading
import queue
import sprecFast as sprec
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

    c.execute("SELECT * FROM speakers WHERE id=?", (speaker_id,))
    speaker = c.fetchone()

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    image_path = f"./Data/{speaker_id}/{speaker_id}.jpg"

    if speaker:
        c.execute("UPDATE speakers SET weight=?, last_recognized=?, image=? WHERE id=?",
                  (speaker[1] + 1, current_time, image_path, speaker_id))
    else:
        c.execute("INSERT INTO speakers (id, weight, last_recognized, image) VALUES (?, ?, ?, ?)",
                  (speaker_id, 1, current_time, image_path))

    conn.commit()
    conn.close()
    json_data = db_to_json()
    save_json_data(json_data)

def db_to_json():
    conn = sqlite3.connect('speakers.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT * FROM speakers")
    rows = c.fetchall()

    json_data = json.dumps([dict(row) for row in rows], indent=2)

    conn.close()
    return json_data

def save_json_data(json_data, filename="speakers.json"):
    with open(filename, "w") as json_file:
        json_file.write(json_data)

latest_speaker_id = None  # Global variable to store the latest speaker id

app = Flask(__name__)
rec = sprec.Recognizer()
audio_queue = queue.Queue()

@app.route('/recognize', methods=['POST'])
def recognize():
    audio_path = request.form['audio_path']
    audio_queue.put(audio_path)
    return jsonify({"status": "success"})

@app.route('/latest_speaker', methods=['GET'])
def get_latest_speaker():
    global latest_speaker_id
    if latest_speaker_id is not None:
        return jsonify({"id": latest_speaker_id})
    else:
        return jsonify({"error": "No speakers found"})

def recognize_speaker(q, recognizer):
    global latest_speaker_id
    while True:
        if not q.empty():
            audio_path = q.get()
            print("Starting recognition:")
            speaker = recognizer.find_speaker(audio_path)
            if speaker:
                print(f"Speaker: {speaker}")
                update_speaker_record(speaker)
                latest_speaker_id = speaker  # Update the global variable
            else:
                print("Speaker not recognized")
                latest_speaker_id = None
            print("Recognition done\n")

if __name__ == '__main__':
    recognition_thread = threading.Thread(target=recognize_speaker, args=(audio_queue, rec))
    recognition_thread.start()

    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
