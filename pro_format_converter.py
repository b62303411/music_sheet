def convert_to_pro_format(position, window_size=5):
    """
    Inputs
      position["frets"]: 6->1 (low E -> high E). Accepts str like 'x24432' or list ['x','2','4','4','3','2']
      Optional:
        position["barres"] : int absolute barre fret (e.g., 2 for Bm).  # authoritative
        position["capo"]   : bool (styling hint only; does not affect fret math)

    Output (VexChords-ready)
      {
        "chord": [[1..6, rel_fret|'x']],            # 1 = high E ... 6 = low E
        "position": base_fret,                      # usually 1
        "barres": [{"fret": rel_fret, "fromString": X, "toString": Y}]
      }
    """
    # --- normalize frets to list in 6->1 order ---
    frets_6_to_1 = position["frets"]
    if isinstance(frets_6_to_1, str):
        frets_6_to_1 = list(frets_6_to_1)
    if len(frets_6_to_1) != 6:
        raise ValueError("frets must be length 6 in low-E->high-E order")

    def fret_to_int(x):
        if x in ("x", "X"): return None
        if isinstance(x, int) and not isinstance(x, bool):  # avoid True/False
            return x
        try:
            return int(x, 16)  # allow hex
        except Exception:
            return int(x)

    abs_frets = [fret_to_int(f) for f in frets_6_to_1]   # indices: [s6,s5,s4,s3,s2,s1]
    playable = [f for f in abs_frets if f and f > 0]

    # --- base position (diagram window), NOT capo-relative ---
    if playable:
        mn, mx = min(playable), max(playable)
        base = 1 if mn <= window_size else mn
        if (mx - base + 1) > window_size:
            base = max(1, mx - window_size + 1)
    else:
        base = 1

    def to_rel(f):
        if f is None: return 'x'
        if f == 0:   return 0
        return f - base + 1

    # --- build chord in 1->6 (high->low) order for VexChords ---
    chord = []
    for s1 in range(1, 7):                # 1..6
        f_abs = abs_frets[6 - s1]         # map 1->index5, 6->index0
        chord.append([s1, to_rel(f_abs)])

    # --- compute barre from absolute 'barres' (int). 'capo' is only a flag, ignored for math ---
    barres = []
    barre_abs = position.get("barres")
    if isinstance(barre_abs, int) and not isinstance(barre_abs, bool) and barre_abs > 0:
        # Which strings are actually fretted at that absolute fret?
        strings_at_barre_1_to_6 = [s1 for s1 in range(1, 7) if abs_frets[6 - s1] == barre_abs]
        if len(strings_at_barre_1_to_6) >= 2:
            barres.append({
                "fret": barre_abs - base + 1,   # relative to diagram base (so Bm -> 2)
                "fromString": max(strings_at_barre_1_to_6),
                "toString":  min(strings_at_barre_1_to_6),
            })

    return {"chord": chord, "position": base, "barres": barres}
