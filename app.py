from flask import Flask, render_template, send_from_directory, abort, jsonify
import os
from chord_db_reader import *
app = Flask(__name__)
SONG_DIR = os.path.join(os.path.dirname(__file__), 'songs')

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

def extract_chords(song_text):
    # This will capture anything inside [ ], including complex chords like Gmaj7, D/F#, etc.
    # Step 2: Define blacklist of known non-chord words (case-insensitive match)
    blacklist = {
        "intro", "verse", "chorus", "bridge", "outro", "solo",
        "instrumental", "pre-chorus", "hook","verse 1","verse 2","verse 3","guitar solo"
    }
    raw_matches =  sorted(set(re.findall(r'\[([^\]]+)\]', song_text)))

    # Step 3: Filter only actual chords
    chords = []
    for match in raw_matches:
        # Strip whitespace and lowercase for comparison
        normalized = match.strip().lower()
        if normalized not in blacklist:
            chords.append(match.strip())

    # Step 4: Return sorted unique list
    return sorted(set(chords))


@app.route("/api/chords")
def chords_api():
    # retourne un JSON automatiquement:contentReference[oaicite:2]{index=2}
    return jsonify(CHORD_SHAPES)


@app.route('/')
def index():
    songs = [f for f in os.listdir(SONG_DIR) if f.endswith('.pro') or f.endswith('.chord')]
    return render_template('home.html', title="ChordieApp", songs=songs)


# Mapping from standard chord name → (key, suffix)
chord_name_to_key_suffix = {
    "A": "Amajor",
    "Am": "Aminor",
    "B": "Bmajor",
    "Bm": "Bminor",
    "C": "Cmajor",
    "D": "Dmajor",
    "Dm": "Dminor",
    "E": "Emajor",
    "Em": "Eminor",
    "F": "Fmajor",
    "F#m":"F#minor",
    "G": "Gmajor",
}

def convert_to_pro_format(position):
    frets = position['frets']
    fingers = position.get('fingers', '')
    string_numbers = range(6, 0, -1)  # Strings 6 (low E) to 1 (high E)

    # Calculate base position for visual library (lowest playable fret)
    playable_frets = [int(f, 16) for f in frets if f not in ('x', 'X', '0')]
    base_position = min(playable_frets) if playable_frets else 1  # Default to 1 if no playable frets

    # Build chord shape with relative fret positions
    chord = []
    for string, fret_char in zip(string_numbers, frets):
        if fret_char in ('x', 'X'):
            fret = 'x'
        else:
            fret = int(fret_char, 16)
            fret = fret - base_position + 1 if fret != 0 else 0  # Convert to relative, keep open strings as 0
        chord.append([string, fret])



    # Detect barres using finger placement
    if fingers and len(frets) == len(fingers):
        finger_fret_map = {}
        for string, fret_char, finger in zip(string_numbers, frets, fingers):
            if fret_char not in ('x', 'X', '0') and finger != '0':
                fret = int(fret_char, 16)
                relative_fret = fret - base_position + 1  # Convert to relative
                finger_fret_map.setdefault(finger, []).append((string, relative_fret))

        barres = []
        for finger, positions in finger_fret_map.items():
            if len(positions) >= 2:  # At least two strings for a barre
                frets_used = {f for _, f in positions}
                if len(frets_used) == 1:  # Same fret across strings
                    fret = frets_used.pop()
                    strings = [s for s, _ in positions]
                    barres.append({
                        "fret": fret,
                        "fromString": min(strings),
                        "toString": max(strings)
                    })
        result = {"chord": chord, "position": base_position,"barres":barres}
        if barres:
            result["barres"] = barres

    return result

@app.route('/song/<filename>')
def show_song(filename):
    filepath = os.path.join(SONG_DIR, filename)
    if not os.path.isfile(filepath):
        abort(404, description="Song not found")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    chords = extract_chords(content)
    song_chords ={}
    converted = {}
    for i in chords:
        if i in chord_name_to_key_suffix:
            key = chord_name_to_key_suffix[i]
            song_chords[i] = full_chord_db[key]
        else:
            song_chords[i] = full_chord_db[i]
        _shapes = []
        for p in song_chords[i]:
            shape = convert_to_pro_format(p)
            _shapes.append(shape)
        converted[i] = _shapes

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
    app.run(debug=True, use_reloader=False)
