
import json
import os
import requests
from pathlib import Path

# Constants
CHORD_DB_BASE = "https://raw.githubusercontent.com/tombatossals/chords-db/master/src/db/guitar/chords"
CHORD_PATTERN = r'\[([A-G][b#]?(m|maj|min|dim|aug|sus|add)?\d*(?:/[A-G])?)\]'
DB_FOLDER = "db/guitar/chords"
OUTPUT_FILE = "chords.json"

full_chord_db = {}
def parse_shape(js_text):
    """Extract a single shape from the JavaScript export."""
    try:
        shape = eval(js_text.replace('true', 'True').replace('false', 'False').replace('null', 'None'))
        return {
            "chord": shape.get("positions", []),
            "position": shape.get("baseFret", 1),
            "barres": [{"fret": b} for b in shape.get("barres", [])]
        }
    except Exception as e:
        print("Error parsing shape:", e)
        return None
def parse_js_like_file(content):
    # Strip 'export default'
    content = re.sub(r'^export\s+default\s+', '', content.strip())

    # Fix unquoted keys (e.g. baseFret: → "baseFret":)
    content = re.sub(r'([{,])\s*([a-zA-Z0-9_]+)\s*:', r'\1 "\2":', content)

    # Replace JS-style booleans/null
    content = content.replace("'", '"')  # Convert single to double quotes
    content = content.replace("True", "true").replace("False", "false").replace("None", "null")

    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        print("❌ JSON decode error:", e)
        return None
import re
import json

def js_object_to_json(js_code):
    # Remove `export default` and trailing semicolon
    js_code = re.sub(r'^export\s+default\s+', '', js_code.strip())
    js_code = re.sub(r';\s*$', '', js_code)

    # Quote unquoted keys
    js_code = re.sub(r'([{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1 "\2":', js_code)

    # Convert single quotes to double quotes
    js_code = js_code.replace("'", '"')

    # Remove trailing commas (before closing array or object)
    js_code = re.sub(r',(\s*[}\]])', r'\1', js_code)

    return json.loads(js_code)

def extract_all_chords():
    chords = {}
    for root, _, files in os.walk(DB_FOLDER):
        for file in files:
            if file.endswith(".js") and not file.__contains__("index"):
                path = os.path.join(root, file)
                with open(path, encoding="utf-8") as f:

                    raw = f.read()
                    parsed = js_object_to_json(raw)

                    if parsed:
                        print("Parsed", len(parsed), "chord shapes.")
                        key = parsed.get('key')  # redundant; we’ll use path
                        suffix = parsed.get('suffix')
                        positions = parsed.get('positions', [])
                        full_chord_db[key+suffix]=positions




def extract_chords_from_pro(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    chords = re.findall(CHORD_PATTERN, content)
    unique_chords = sorted(set([c[0] for c in chords]))
    return unique_chords

def download_chord_file(letter, chord):
    url = f"{CHORD_DB_BASE}/{letter}/{chord}.js"
    print(f"Fetching: {url}")
    r = requests.get(url)
    if r.status_code == 200:
        return r.text
    return None

def extract_chord_shape(js_code):
    match = re.search(r'export default (\[.*\]);', js_code, re.DOTALL)
    if not match:
        return None
    try:
        json_like = match.group(1)
        return json.loads(json_like)
    except Exception as e:
        print("Failed to parse shape:", e)
        return None

def normalize_chord_name(chord):
    return chord.replace("maj", "major").replace("min", "minor").replace(" ", "")

def fetch_and_parse_chords(chords):
    parsed = {}
    for chord in chords:
        letter = chord[0].upper()
        name = normalize_chord_name(chord)
        js_code = download_chord_file(letter, name)
        if js_code:
            shape = extract_chord_shape(js_code)
            if shape:
                parsed[chord] = shape[0]  # only keep the first shape for simplicity
    return parsed

def save_to_json(data, path="parsed_chords.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# Main flow
if __name__ == "__main__":
    pro_file = "song.pro"  # Replace with your actual file
    chords = extract_chords_from_pro(pro_file)
    print("Chords found:", chords)
    parsed_shapes = fetch_and_parse_chords(chords)
    save_to_json(parsed_shapes)
    print(f"Saved {len(parsed_shapes)} chord shapes to parsed_chords.json")
