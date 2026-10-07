"""Articulatory-feature-based IPA phone mapping used by CrossPhon."""

import argparse
from pathlib import Path

class IPASymbol:
    def __init__(self, symbol, manner, place, voiced, consonant, diacritic=None):
        self.symbol = symbol      # visible symbol (keeps ':' vs 'ː' as in input)
        self.manner = manner
        self.place = place
        self.voiced = voiced
        self.consonant = consonant
        self.diacritic = diacritic or []  # canonical diacritics (e.g. ':' -> 'ː')
    
    def __str__(self):
        return (
            f"Symbol: {self.symbol}, Manner: {self.manner}, "
            f"Place: {self.place}, Voiced: {self.voiced}, "
            f"Consonant: {self.consonant}, Diacritic: {self.diacritic}"
        )

def step_wise_distance(ipa1, ipa2):
    if ipa1.consonant != ipa2.consonant:
        return 100, 100
    manner_diff = abs(ipa1.manner - ipa2.manner)
    place_diff  = abs(ipa1.place  - ipa2.place)
    voiced_diff = abs(ipa1.voiced - ipa2.voiced)
    total_distance   = manner_diff + place_diff + voiced_diff
    changed_attributes = manner_diff * 0.01 + place_diff * 0.1 + voiced_diff * 1
    return total_distance, changed_attributes

def common_start(sa, sb):
    """returns the longest common substring from the beginning of sa and sb"""
    def _iter():
        for a, b in zip(sa, sb):
            if a == b:
                yield a
            else:
                return
    return ''.join(_iter())

# Helper: normalize symbols so ':' and 'ː' are treated as the same
def normalize_symbol_string(s: str) -> str:
    return s.replace(':', 'ː')

# Hardcoded dictionary for IPA symbols with their axis attributes
ipa_attributes = {
    'p': (0, 0, 0, True),
    'b': (0, 0, 1, True),
    't': (0, 3, 0, True),
    'd': (0, 3, 1, True),
    'ʈ': (0, 5, 0, True),
    'ɖ': (0, 5, 1, True),
    'c': (0, 6, 0, True),
    'ɟ': (0, 6, 1, True),
    'k': (0, 7, 0, True),
    'ɡ': (0, 7, 1, True),
    'q': (0, 8, 0, True),
    'ɢ': (0, 8, 1, True),
    'ʔ': (0, 10, 0, True),
    'm': (1, 0, 1, True),
    'ɱ': (1, 1, 1, True),
    'n': (1, 3, 1, True),
    'ɳ': (1, 5, 1, True),
    'ɲ': (1, 6, 1, True),
    'ŋ': (1, 7, 1, True),
    'ɴ': (1, 8, 1, True),
    'ʙ': (2, 0, 1, True),
    'r': (2, 3, 1, True),
    'ʀ': (2, 8, 1, True),
    'ⱱ': (3, 1, 1, True),
    'ɾ': (3, 3, 1, True),
    'ɽ': (3, 5, 1, True),
    'ɸ': (4, 0, 0, True),
    'β': (4, 0, 1, True),
    'f': (4, 1, 0, True),
    'v': (4, 1, 1, True),
    'θ': (4, 2, 0, True),
    'ð': (4, 2, 1, True),
    's': (4, 3, 0, True),
    'z': (4, 3, 1, True),
    'ʃ': (4, 4, 0, True),
    'ʒ': (4, 4, 1, True),
    'ʂ': (4, 5, 0, True),
    'ʐ': (4, 5, 1, True),
    'ç': (4, 6, 0, True),
    'ʝ': (4, 6, 1, True),
    'x': (4, 7, 0, True),
    'ɣ': (4, 7, 1, True),
    'χ': (4, 8, 0, True),
    'ʁ': (4, 8, 1, True),
    'ħ': (4, 9, 0, True),
    'ʕ': (4, 9, 1, True),
    'h': (4, 10, 0, True),
    'ɦ': (4, 10, 1, True),
    'ɬ': (5, 3, 0, True),
    'ɮ': (5, 3, 1, True),
    'ʋ': (6, 1, 1, True),
    'ɹ': (6, 3, 1, True),
    'ɻ': (6, 5, 1, True),
    'j': (6, 6, 1, True),
    'ɰ': (6, 7, 1, True),
    'l': (7, 3, 1, True),
    'ɭ': (7, 5, 1, True),
    'ʎ': (7, 6, 1, True),
    'ʟ': (7, 7, 1, True),
    'ʘ': (8, 0, 0, True),
    'ǀ': (8, 2, 0, True),
    'ǃ': (8, 4, 0, True),
    'ǂ': (8, 6, 0, True),
    'ǁ': (8, 3, 0, True),
    'ɓ': (9, 0, 1, True),
    'ɗ': (9, 3, 1, True),
    'ʄ': (9, 6, 1, True),
    'ɠ': (9, 7, 1, True),
    'ʛ': (9, 8, 1, True),
    'ʍ': (4, 1, 0, True),
    'w': (6, 7, 1, True),
    'ɥ': (6, 6, 1, True),
    'ʜ': (4, 10, 0, True),
    'ʢ': (4, 10, 1, True),
    'ʡ': (0, 10, 0, True),
    'ɕ': (4, 6, 0, True),
    'ʑ': (4, 6, 1, True),
    'ɺ': (3, 3, 1, True),
    'ɧ': (4, 7, 0, True),
    'i': (0, 0, 0, False),
    'y': (0, 0, 1, False),
    'ɨ': (0, 1, 0, False),
    'ʉ': (0, 1, 1, False),
    'ɯ': (0, 2, 0, False),
    'u': (0, 2, 1, False),
    'ɪ': (1, 0, 0, False),
    'ʏ': (1, 0, 1, False),
    'ʊ': (1, 2, 0, False),
    'e': (2, 0, 0, False),
    'ø': (2, 0, 1, False),
    'ɘ': (2, 1, 0, False),
    'ɵ': (2, 1, 1, False),
    'ɤ': (2, 2, 0, False),
    'o': (2, 2, 1, False),
    'ə': (3, 1, 0, False),
    'ɚ': (3, 1, 0, False),
    'ɛ': (4, 0, 0, False),
    'œ': (4, 0, 1, False),
    'ɜ': (4, 1, 0, False),
    'ɝ': (4, 1, 0, False),
    'ɞ': (4, 1, 1, False),
    'ʌ': (4, 2, 0, False),
    'ɔ': (4, 2, 1, False),
    'æ': (5, 0, 0, False),
    'ɐ': (5, 1, 0, False),
    'a': (6, 0, 0, False),
    'ɶ': (6, 0, 1, False),
    'ɑ': (6, 2, 0, False),
    'ɒ': (6, 2, 1, False),
    'ɫ': (7, 9, 1, True)
}

# Hardcoded dictionary for diacritics
# NOTE: ':' and 'ː' now share the same canonical value 'ː'
diacritic_encoding = {
    'ː': "ː",   # IPA long
    ':': "ː",   # ASCII colon, treated as the same as IPA long for comparison
    'ʼ': "ʼ",
    '̥': "̥",
    '̬': "̬",
    'ʰ': "ʰ",
    '̹': "̹",
    '̜': "̜",
    '̟': "̟",
    '̠': "̠",
    '̈': "̈",
    '̽': "̽",
    '̩': "̩",
    '̯': "̯",
    '˞': "˞",
    '̤': "̤",
    '̰': "̰",
    '̼': "̼",
    'ʷ': "ʷ",
    'ʲ': "ʲ",
    'ˠ': "ˠ",
    'ˤ': "ˤ",
    '̴': "̴",
    '̝': "̝",
    '̞': "̞",
    '̘': "̘",
    '̙': "̙",
    '̪': "̪",
    '̺': "̺",
    '̻': "̻",
    '̃': "̃",
    'ⁿ': "ⁿ",
    'ˡ': "ˡ",
    '̚': "̚",
    'ˑ': "ˑ",
    '̆': "̆",   # combining breve
    '⁓': "⁓",
    '‖': "‖",
    '‿': "‿",
    '͡': "͡",
    '̍': "̍",
    'ˀ': "ˀ",
}

def tokenize_with_diacritics(symbol_str):
    """
    Turn a string like 'aːu' or 'a:u' or 't͡sʰ' or 'ă' into a list of IPASymbol tokens where:
      - each base letter gets its own diacritics attached (symbol + diacritics)
      - diacritics are NOT dropped or moved
      - ':' and 'ː' are treated the same in diacritic list (canonical 'ː'),
        but the visible symbol keeps the original character as in the file
      - 'ă' is normalized to 'a' + combining breve '̆'
    """
    # Normalize precomposed 'ă' to 'a' + combining breve '̆'
    symbol_str = symbol_str.replace('ă', 'ă')

    tokens = []
    current = None  # (base_char, diacritics_list, visible_symbol_string)

    for ch in symbol_str:
        if ch in diacritic_encoding:
            # diacritic attaches to the current base
            if current is None:
                # orphan diacritic; skip safely
                continue
            base, dias, vis = current
            canon = diacritic_encoding[ch]   # canonical form for comparison
            dias.append(canon)
            vis += ch                        # keep the raw character in the visible string
            current = (base, dias, vis)
        else:
            # base IPA symbol
            if current is not None:
                base, dias, vis = current
                if base in ipa_attributes:
                    manner, place, voiced, consonant = ipa_attributes[base]
                    tokens.append(IPASymbol(vis, manner, place, voiced, consonant, dias))
            # start new token
            if ch not in ipa_attributes:
                current = None
                continue
            manner, place, voiced, consonant = ipa_attributes[ch]
            current = (ch, [], ch)

    # flush last token
    if current is not None:
        base, dias, vis = current
        if base in ipa_attributes:
            manner, place, voiced, consonant = ipa_attributes[base]
            tokens.append(IPASymbol(vis, manner, place, voiced, consonant, dias))

    return tokens

def create_mapping(source_file, target_file, output_file):
    """Map every source inventory entry to the closest target entry.

    Inventory files contain one IPA phone or phone sequence per line. The
    resulting mapping is written as UTF-8, tab-separated source/target pairs.
    The mapping dictionary is returned for callers and tests.
    """
    mapping = {}
    
    # Build source lists
    source_ipas = []
    source_ipa_combination = []
    with open(source_file, 'r', encoding='utf-8') as source:
        for line in source:
            symbol = line.strip()
            if not symbol:
                continue
            tokens = tokenize_with_diacritics(symbol)
            if len(tokens) > 1:
                source_ipa_combination.append(tokens)
            elif len(tokens) == 1:
                source_ipas.append(tokens[0])

    # Build target lists
    target_ipas = []
    target_ipa_combination = []
    with open(target_file, 'r', encoding='utf-8') as target:
        for line in target:
            symbol = line.strip()
            if not symbol:
                continue
            tokens = tokenize_with_diacritics(symbol)
            if len(tokens) > 1:
                target_ipa_combination.append(tokens)
            elif len(tokens) == 1:
                target_ipas.append(tokens[0])

    # -------- mapping for single IPA symbols --------
    for source_ipa in source_ipas:
        mapped_ipa = None

        # exact match including diacritics and consonant/vowel type
        for target_ipa in target_ipas:
            if (
                normalize_symbol_string(source_ipa.symbol) ==
                normalize_symbol_string(target_ipa.symbol)
                and source_ipa.diacritic == target_ipa.diacritic
                and source_ipa.consonant == target_ipa.consonant
            ):
                # write out target_ipa.symbol as-is (keeps ':' or 'ː' from target file)
                mapping[source_ipa.symbol] = target_ipa.symbol
                mapped_ipa = target_ipa
                break
        if mapped_ipa:
            continue

        # partial diacritic overlap on same base and type
        for target_ipa in target_ipas:
            if (
                source_ipa.symbol and target_ipa.symbol and
                source_ipa.symbol[0] == target_ipa.symbol[0] and
                source_ipa.consonant == target_ipa.consonant
            ):
                if not source_ipa.diacritic or not target_ipa.diacritic:
                    continue
                if any(dia in target_ipa.diacritic for dia in source_ipa.diacritic):
                    mapping[source_ipa.symbol] = target_ipa.symbol
                    mapped_ipa = target_ipa
                    break
        if mapped_ipa:
            continue

        # step-wise distance fallback (same type only)
        min_distance = float('inf')
        min_change = float('inf')
        for target_ipa in target_ipas:
            if source_ipa.consonant == target_ipa.consonant:
                distance, change = step_wise_distance(source_ipa, target_ipa)
                if distance < min_distance or (distance == min_distance and change < min_change):
                    min_distance = distance
                    min_change = change
                    mapped_ipa = target_ipa

        if mapped_ipa is None:
            raise ValueError(
                f"No compatible target phone for source phone {source_ipa.symbol!r}"
            )
        mapping[source_ipa.symbol] = mapped_ipa.symbol

    # -------- mapping for combination IPA symbols --------
    potential = {}
    for source_combo in source_ipa_combination:
        source_symbol = ''.join(tok.symbol for tok in source_combo)
        source_symbol_norm = normalize_symbol_string(source_symbol)
        mapped_ipa = None
        source_len = len(source_combo)
        candidates = []

        # 1) exact combo match (position-wise same base initials)
        for target_combo in target_ipa_combination:
            if len(target_combo) == source_len:
                target_symbol = ''.join(tok.symbol for tok in target_combo)
                target_symbol_norm = normalize_symbol_string(target_symbol)
                flag = True
                for i in range(source_len):
                    if source_combo[i].symbol[0] != target_combo[i].symbol[0]:
                        flag = False
                        break
                if flag and source_symbol_norm == target_symbol_norm:
                    mapped_ipa = target_symbol
                    mapping[source_symbol] = mapped_ipa
                    break
        if mapped_ipa:
            continue

        # 2) partial diacritic overlap in position-wise comparable combos
        for target_combo in target_ipa_combination:
            if len(target_combo) == source_len:
                target_symbol = ''.join(tok.symbol for tok in target_combo)
                flag = True
                for i in range(source_len):
                    if source_combo[i].symbol[0] != target_combo[i].symbol[0]:
                        flag = False
                        break
                if flag:
                    if source_combo[0].diacritic and target_combo[0].diacritic:
                        if any(d in target_combo[0].diacritic for d in source_combo[0].diacritic):
                            mapped_ipa = target_symbol
                            mapping[source_symbol] = mapped_ipa
                            break
        if mapped_ipa:
            continue

        # 3) sliding/length-mismatch distance (average over aligned pairs)
        min_distance = float('inf')
        min_change = float('inf')

        def avg_dist(src_slice, tgt_slice):
            dist_sum = 0
            chg_sum = 0
            for a, b in zip(src_slice, tgt_slice):
                d, c = step_wise_distance(a, b)
                dist_sum += d
                chg_sum += c
            n = max(1, len(tgt_slice))
            return dist_sum / n, chg_sum / n

        for target_combo in target_ipa_combination:
            target_symbol = ''.join(tok.symbol for tok in target_combo)
            target_len = len(target_combo)

            if target_len < source_len:
                for i in range(source_len - target_len + 1):
                    distance, change = avg_dist(source_combo[i:i+target_len], target_combo)
                    better = (distance < min_distance or
                              (distance == min_distance and change < min_change))
                    if better:
                        candidates = [target_symbol] if distance < min_distance else candidates + [target_symbol]
                        mapped_ipa = target_symbol
                        min_distance = distance
                        min_change = change
                        if source_combo[0].consonant:
                            if normalize_symbol_string(target_symbol[-1]) == normalize_symbol_string(source_symbol[-1]):
                                mapped_ipa = target_symbol
                        else:
                            if normalize_symbol_string(target_symbol[0]) == normalize_symbol_string(source_symbol[0]):
                                mapped_ipa = target_symbol

            elif target_len > source_len:
                for i in range(target_len - source_len + 1):
                    distance, change = avg_dist(source_combo, target_combo[i:i+source_len])
                    better = (distance < min_distance or
                              (distance == min_distance and change < min_change))
                    if better:
                        candidates = [target_symbol] if distance < min_distance else candidates + [target_symbol]
                        mapped_ipa = target_symbol
                        min_distance = distance
                        min_change = change
                        if source_combo[0].consonant:
                            if normalize_symbol_string(target_symbol[-1]) == normalize_symbol_string(source_symbol[-1]):
                                mapped_ipa = target_symbol
                        else:
                            if normalize_symbol_string(target_symbol[0]) == normalize_symbol_string(source_symbol[0]):
                                mapped_ipa = target_symbol

            else:
                distance, change = avg_dist(source_combo, target_combo)
                better = (distance < min_distance or
                          (distance == min_distance and change < min_change))
                if better:
                    candidates = [target_symbol] if distance < min_distance else candidates + [target_symbol]
                    mapped_ipa = target_symbol
                    min_distance = distance
                    min_change = change
                    if source_combo[0].consonant:
                        if normalize_symbol_string(target_symbol[-1]) == normalize_symbol_string(source_symbol[-1]):
                            mapped_ipa = target_symbol
                    else:
                        if normalize_symbol_string(target_symbol[0]) == normalize_symbol_string(source_symbol[0]):
                            mapped_ipa = target_symbol

        # 4) fallback: compare first/last element to all single targets
        for target_ipa in target_ipas:
            if source_combo[0].consonant:
                distance, change = step_wise_distance(source_combo[-1], target_ipa)
            else:
                distance, change = step_wise_distance(source_combo[0], target_ipa)
            if distance + source_len < min_distance or (
                distance + source_len == min_distance and change < min_change
            ):
                min_distance = distance + source_len
                min_change = change
                mapped_ipa = target_ipa.symbol

        if mapped_ipa is None:
            raise ValueError(f"No compatible target phone for source sequence {source_symbol!r}")
        mapping[source_symbol] = mapped_ipa
        if len(candidates) > 1:
            potential[source_symbol] = candidates

    # Store mapping results in a new text file
    flag = False
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open('w', encoding='utf-8') as result_file:
        sort = dict(sorted(mapping.items()))
        for source_symbol, target_symbol in sort.items():
            if source_symbol in potential:
                flag = True
                temp = ' '.join(potential[source_symbol])
                print(
                    "The mapping for " + source_symbol + " is now " + target_symbol +
                    "; just a note that all potential mappings are: " + temp
                )
            result_file.write(f"{source_symbol}\t{target_symbol}\n")
    if flag:
        print(f"Review ambiguous mappings in {output_path} if needed.")
    return mapping

def main():
    parser = argparse.ArgumentParser(
        description="Generate a CrossPhon segmental mapping between two IPA inventories."
    )
    parser.add_argument("source_inventory", help="One source IPA unit per line")
    parser.add_argument("target_inventory", help="One target IPA unit per line")
    parser.add_argument("output_mapping", help="Destination TSV mapping")
    args = parser.parse_args()
    create_mapping(args.source_inventory, args.target_inventory, args.output_mapping)


if __name__ == "__main__":
    main()
