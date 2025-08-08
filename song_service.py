import os
import re

from flask import abort

from chord_db_reader import full_chord_db
from pro_format_converter import convert_to_pro_format

SONG_DIR = os.path.join(os.path.dirname(__file__), 'songs')

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

def get_songs():
    songs = [f for f in os.listdir(SONG_DIR) if f.endswith('.pro') or f.endswith('.chord')]
    return songs

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


def get_song(filename):
    filepath = os.path.join(SONG_DIR, filename)
    if not os.path.isfile(filepath):
        abort(404, description="Song not found")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    chords = extract_chords(content)
    song_chords = {}
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
    return content,song_chords,converted ,chords
