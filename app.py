from flask import Flask, render_template, send_from_directory, abort, jsonify
import os
from chord_db_reader import *
from song_service import get_songs, get_song

app = Flask(__name__)


# dictionnaire de positions : chaque accord est une liste de [corde, frette]
CHORD_SHAPES = {
    "G": {"chord": [[1, 3], [2, 0], [3, 0], [4, 0], [5, 2], [6, 3]]},
    "A": {"chord": [[1, 0], [2, 2], [3, 2], [4, 2], [5, 0], [6, 'x']]},
    "E": {"chord": [[1, 0], [2, 0], [3, 1], [4, 2], [5, 2], [6, 0]]},
    "D": {"chord": [[1, 2], [2, 3], [3, 2], [4, 0], [5, 'x'], [6, 'x']]},
    "Em7": {"chord": [[1, 0], [2, 3], [3, 0], [4, 2], [5, 2], [6, 0]]},
    "Cadd9": {"chord": [[1, 3], [2, 3], [3, 0], [4, 2], [5, 3], [6, 'x']]},
    "Dsus4": {"chord": [[1, 3], [2, 3], [3, 2], [4, 0], [5, 'x'], [6, 'x']]},
    # Accords spécifiques à "Time"[{ "fret": 2, "fromString": 6, "toString": 1 }]
    "F#m": {"position": 1, "chord": [[1, 2], [2, 2], [3, 2], [4, 4], [5, 4], [6, 2]],
            "barres": [{"fret": 2, "fromString": 6, "toString": 1}]},  # barré 2
    "Dmaj7": {"chord": [[1, 2], [2, 2], [3, 2], [4, 0], [5, 'x'], [6, 'x']]},
    "Amaj7": {"chord": [[1, 0], [2, 2], [3, 1], [4, 2], [5, 0], [6, 'x']]},
    "C#m7": {"chord": [[1, 4], [2, 5], [3, 4], [4, 6], [5, 4], [6, 'x']]},
    "Bm7": {"chord": [[1, 2], [2, 0], [3, 2], [4, 0], [5, 2], [6, 'x']]},
    "F/B": {"chord": [[1, 1], [2, 1], [3, 2], [4, 3], [5, 2], [6, 'x']]},  # aka Fadd#11/B
    "Emadd9": {"chord": [[1, 0], [2, 0], [3, 4], [4, 2], [5, 2], [6, 0]]},
    "Em7": {"chord": [[1, 0], [2, 3], [3, 0], [4, 0], [5, 2], [6, 0]]},
    "Cmaj7": {"chord": [[1, 0], [2, 0], [3, 0], [4, 2], [5, 3], [6, 'x']]},
    "Fmaj7": {"chord": [[1, 0], [2, 1], [3, 2], [4, 3], [5, 'x'], [6, 'x']]},
    "G": {"chord": [[1, 3], [2, 0], [3, 0], [4, 0], [5, 2], [6, 3]]},
    "D7#9": {"chord": [[1,1], [2, 1], [3, 2], [4, 0], [5, 'x'], [6, 'x']]},
    "D7b9": { "position": 10,
              "chord": [[6, 1], [5, 3], [4,1 ], [3, 2], [2, 1], [1, 2]],
              "barres": [{"fret": 1, "fromString": 6, "toString": 1}]},
    "Bm": {"chord": [[1, 2], [2, 3], [3, 4], [4, 4], [5, 2], [6, 'x']],
           "barres": [{"fret": 2, "fromString": 5, "toString": 1}]},  # barré 2
}




@app.route("/api/chords")
def chords_api():
    # retourne un JSON automatiquement:contentReference[oaicite:2]{index=2}
    return jsonify(CHORD_SHAPES)


@app.route('/')
def index():
    songs = get_songs()
    return render_template('home.html', title="ChordieApp", songs=songs)

@app.route('/song/<filename>')
def show_song(filename):
    content,song_chords,converted ,chords= get_song(filename)

    return render_template(
        'song.html',
        song_title=filename.replace(".pro", "").replace(".chord", ""),
        song_content=content,
        song_chords=chords,
        chords_positions=song_chords,
        converted=converted
    )


if __name__ == '__main__':
    extract_all_chords()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), threaded=True)
