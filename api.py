from flask import Flask, request, jsonify
import threading
import queue
import sprec
import record

import sqlite3
from datetime import datetime

# Database setup
def create_db():
    conn = sqlite3.connect('speakers.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS speakers
                 (id TEXT PRIMARY KEY, weight INTEGER, last_recognized TEXT)''')
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

    if speaker:
        # Update the existing speaker's weight and last_recognized timestamp
        c.execute("UPDATE speakers SET weight=?, last_recognized=? WHERE id=?",
                  (speaker[1] + 1, current_time, speaker_id))
    else:
        # Insert a new speaker record
        c.execute("INSERT INTO speakers (id, weight, last_recognized) VALUES (?, ?, ?)",
                  (speaker_id, 1, current_time))

    conn.commit()
    conn.close()



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
