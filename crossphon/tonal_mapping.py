"""Combine a CrossPhon segmental mapping with Chao-tone mapping."""

import argparse
from pathlib import Path

# ----------------------------
# Tone marker definitions
# ----------------------------
tone_map = {
    '˩': 1,  # Lowest
    '˨': 2,
    '˧': 3,
    '˦': 4,
    '˥': 5   # Highest
}
tone_symbols = set(tone_map.keys())

# ----------------------------
# Utilities
# ----------------------------
def split_ipa_and_tone(ipa_tonal):
    """
    Splits IPA string into phone and tone (including diacritics).
    Also normalizes 'ă' → 'ă'.

    Note: This function assumes tone marks (˩˨˧˦˥) only appear in the tonal suffix,
    so it splits at the first occurrence of any tone mark.
    """
    ipa_tonal = ipa_tonal.replace("ă", "ă")

    for i, char in enumerate(ipa_tonal):
        if char in tone_symbols:
            return ipa_tonal[:i], ipa_tonal[i:]
    return ipa_tonal, ""


def _tone_only(tone):
    return ''.join(c for c in tone if c in tone_symbols)


def classify_tone_feature(tone):
    """
    tone is expected to be like 'a˨˩˦' (dummy segment + tone marks).
    """
    tone_only = ''.join(c for c in tone[1:] if c in tone_symbols)
    if len(tone_only) <= 1:
        return 'none'
    if all(tone_map[tone_only[i]] < tone_map[tone_only[i + 1]] for i in range(len(tone_only) - 1)):
        return 'rising'
    if all(tone_map[tone_only[i]] > tone_map[tone_only[i + 1]] for i in range(len(tone_only) - 1)):
        return 'falling'
    if all(tone_map[tone_only[i]] == tone_map[tone_only[i + 1]] for i in range(len(tone_only) - 1)):
        return 'flat'
    if len(tone_only) >= 3:
        if tone_map[tone_only[0]] > tone_map[tone_only[1]] and tone_map[tone_only[-1]] > tone_map[tone_only[-2]]:
            return 'concave'
        if tone_map[tone_only[0]] < tone_map[tone_only[1]] and tone_map[tone_only[-1]] < tone_map[tone_only[-2]]:
            return 'convex'
    return 'unknown'


def degree_of_change(tone):
    tone_only = ''.join(c for c in tone[1:] if c in tone_symbols)
    if len(tone_only) < 2:
        return 0
    return abs(tone_map[tone_only[0]] - tone_map[tone_only[-1]])


def tone_distance(tone1, tone2):
    t1 = ''.join(c for c in tone1[1:] if c in tone_symbols)
    t2 = ''.join(c for c in tone2[1:] if c in tone_symbols)
    max_len = max(len(t1), len(t2))
    t1 = t1.ljust(max_len, '˧')
    t2 = t2.ljust(max_len, '˧')
    return sum(abs(tone_map[a] - tone_map[b]) for a, b in zip(t1, t2))


def load_file(filepath):
    with open(filepath, encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


def load_mapping(filepath):
    mapping = {}
    with open(filepath, encoding='utf-8') as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            if '\t' in s:
                src, tgt = s.split('\t')
            elif ' ' in s:
                src, tgt = s.split()
            else:
                continue
            mapping[src] = tgt
    return mapping


# ----------------------------
# Toneless-source fallback selection
# ----------------------------
def _is_flat_at_level(tone, lvl_char):
    t_only = _tone_only(tone)
    # Level tone can be length 1 or more (e.g., ˨ or ˨˨˨)
    return len(t_only) >= 1 and all(c == lvl_char for c in t_only)


def _is_falling(tone):
    t_only = _tone_only(tone)
    if len(t_only) < 2:
        return False
    return all(tone_map[t_only[i]] > tone_map[t_only[i + 1]] for i in range(len(t_only) - 1))


def _choose_best_flat_at_level(candidates, lvl_char):
    """
    Among flat tones at the same pitch level, prefer the *simplest* level tone.
    IMPORTANT: do NOT assume level tones are length 2. They can be length 1+.
    Strategy:
        - prefer the shortest length (e.g., ˨ beats ˨˨)
        - tie-breaker: keep stable order
    """
    best = None
    best_len = float('inf')
    for tone in candidates:
        t_only = _tone_only(tone)
        if len(t_only) < best_len:
            best_len = len(t_only)
            best = tone
    return best


def _choose_best_falling(candidates):
    """
    Prefer falling tones first for toneless→tonal mapping.
    Strategy (kept close to your original):
        - maximize degree_of_change
        - tie-breaker: choose the one with smaller tone_distance to a default falling reference
          (we'll use a generic 'a˥˩' padded logic via tone_distance; if lengths differ, padding handles it)
    """
    best = None
    best_deg = -1
    best_dist = float('inf')

    # Reference is arbitrary; used only as a tie-breaker across equal degree.
    ref = 'a˥˩'
    for tone in candidates:
        deg = degree_of_change('a' + tone)
        dist = tone_distance(ref, 'a' + tone)
        if deg > best_deg or (deg == best_deg and dist < best_dist):
            best_deg = deg
            best_dist = dist
            best = tone
    return best or ""


def _choose_tone_for_toneless(mapped_phone, target_tonal):
    """
    If the mapped phone exists in the target with a non-tonal form, output non-tonal.
    Otherwise, if mapping MUST pick a tone, prefer:
        1) Falling tones (user preference)
        2) Level tones at a preferred level (˩ ˨ ˧ ˦ ˥), where "level" can be length 1+
        3) Otherwise, no tone
    """
    same_phone = []
    for tgt in target_tonal:
        tgt_phone, tgt_tone = split_ipa_and_tone(tgt)
        if tgt_phone == mapped_phone:
            same_phone.append((tgt_tone, tgt))

    # If the target has a non-tonal version for this phone, prefer it.
    for tone, _ in same_phone:
        if tone == "":
            return ""

    # (NEW) Prefer falling tones first when forced to add tone
    falling = [tone for tone, _ in same_phone if _is_falling(tone)]
    if falling:
        return _choose_best_falling(falling)

    # Then prefer a level tone (length 1+), with level priority low→high
    priority = ['˩', '˨', '˧', '˦', '˥']
    for lvl in priority:
        flats = [tone for tone, _ in same_phone if _is_flat_at_level(tone, lvl)]
        if flats:
            return _choose_best_flat_at_level(flats, lvl)

    return ""


# ----------------------------
# Tone mapping with feature-first priority (unchanged)
# ----------------------------
def map_tone(source_tone, target_tonal):
    """
    Map a source tone string (e.g., '˨˩˦') to the closest tone string available in target_tonal.
    This already prefers mapping level→level because 'flat' is a feature class.
    """
    if source_tone == "":
        return ""

    source_feature = classify_tone_feature('a' + source_tone)
    source_degree = degree_of_change('a' + source_tone)

    best_match = None
    best_feature_match = None
    best_distance = float('inf')
    best_degree_diff = float('inf')

    for tgt in target_tonal:
        _, tgt_tone = split_ipa_and_tone(tgt)
        if tgt_tone == "":
            continue

        target_feature = classify_tone_feature('a' + tgt_tone)
        target_degree = degree_of_change('a' + tgt_tone)
        dist = tone_distance('a' + source_tone, 'a' + tgt_tone)

        if target_feature == source_feature:
            degree_diff = abs(source_degree - target_degree)
            if (best_feature_match is None or
                degree_diff < best_degree_diff or
                (degree_diff == best_degree_diff and dist < best_distance)):
                best_match = tgt_tone
                best_feature_match = True
                best_degree_diff = degree_diff
                best_distance = dist

        elif best_feature_match is None:
            if dist < best_distance:
                best_match = tgt_tone
                best_distance = dist

    return best_match or ""


# ============================================================
# ⭐ SANITY CHECK: ensure mapped phone exists in target list
# ============================================================
def enforce_sanity(mapped_phone, mapped_tone, target_tonal):
    """
    Rule:
        If mapped_phone+mapped_tone does NOT exist in target,
        AND the target only has the non-tonal version,
        → output the non-tonal one.

        If target has *any* tonal variants, do NOT override.
    """
    full = mapped_phone + mapped_tone

    # Build exact phone→tones map
    phone_to_tones = {}
    for tgt in target_tonal:
        tp, tt = split_ipa_and_tone(tgt)
        phone_to_tones.setdefault(tp, []).append(tt)

    # Case 1: phone not in target at all → leave unchanged
    if mapped_phone not in phone_to_tones:
        return full

    tones = phone_to_tones[mapped_phone]

    # Case 2: exact match exists → keep
    if mapped_tone in tones:
        return full

    # Case 3: NO tone exists in target → force toneless
    if tones == [""] or ("" in tones and len(tones) == 1):
        return mapped_phone  # strip tone

    # Case 4: target HAS tonal variants → DO NOT override
    return full


# ----------------------------
# Main combiner
# ----------------------------
def combine_mapping(source_file, target_file, mapping_file, output_file):
    source_tonal = load_file(source_file)
    target_tonal = load_file(target_file)
    phone_mapping = load_mapping(mapping_file)

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    written = {}
    with output_path.open('w', encoding='utf-8') as out:
        for src_full in source_tonal:
            src_phone, src_tone = split_ipa_and_tone(src_full)

            if src_phone not in phone_mapping:
                continue

            mapped_phone = phone_mapping[src_phone]

            if src_tone == "":
                mapped_tone = _choose_tone_for_toneless(mapped_phone, target_tonal)
            else:
                mapped_tone = map_tone(src_tone, target_tonal)

            # ⭐ Apply sanity check
            safe_output = enforce_sanity(mapped_phone, mapped_tone, target_tonal)

            out.write(f"{src_full}\t{safe_output}\n")
            written[src_full] = safe_output

    print(f"Combined phone-tone mapping complete. Results written to '{output_path}'")
    return written


# ----------------------------
# Run
# ----------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Combine a segmental mapping with CrossPhon-Tonal tone mapping."
    )
    parser.add_argument("source_tonal_inventory")
    parser.add_argument("target_tonal_inventory")
    parser.add_argument("segmental_mapping")
    parser.add_argument("output_mapping")
    args = parser.parse_args()
    combine_mapping(
        args.source_tonal_inventory,
        args.target_tonal_inventory,
        args.segmental_mapping,
        args.output_mapping,
    )


if __name__ == "__main__":
    main()
