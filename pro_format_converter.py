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