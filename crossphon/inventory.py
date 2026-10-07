"""Extract segmental and tonal IPA inventories from an MFA dictionary."""

import argparse
from pathlib import Path

TONE_MARKS = frozenset("˩˨˧˦˥")


def remove_tone_marks(symbol):
    return "".join(character for character in symbol if character not in TONE_MARKS)


def extract_inventories(dictionary_path, segmental_output, tonal_output=None):
    """Extract unique pronunciation units and optionally retain tonal forms."""
    segmental = set()
    tonal = set()
    has_tones = False

    with Path(dictionary_path).open(encoding="utf-8") as dictionary:
        for raw_line in dictionary:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            pronunciation = line.split("\t")[-1].strip()
            if not pronunciation:
                continue
            for symbol in pronunciation.split():
                tonal.add(symbol)
                segmental.add(remove_tone_marks(symbol))
                has_tones = has_tones or any(mark in symbol for mark in TONE_MARKS)

    segmental_path = Path(segmental_output)
    segmental_path.parent.mkdir(parents=True, exist_ok=True)
    segmental_path.write_text(
        "".join(f"{item}\n" for item in sorted(segmental)), encoding="utf-8"
    )

    if tonal_output is not None:
        tonal_path = Path(tonal_output)
        tonal_path.parent.mkdir(parents=True, exist_ok=True)
        tonal_path.write_text(
            "".join(f"{item}\n" for item in sorted(tonal)), encoding="utf-8"
        )

    return {"segmental": segmental, "tonal": tonal, "has_tones": has_tones}


def main():
    parser = argparse.ArgumentParser(
        description="Extract unique IPA units from an MFA pronunciation dictionary."
    )
    parser.add_argument("dictionary")
    parser.add_argument("segmental_output")
    parser.add_argument(
        "--tonal-output",
        help="Optional output retaining Chao tone letters",
    )
    args = parser.parse_args()
    result = extract_inventories(args.dictionary, args.segmental_output, args.tonal_output)
    print(f"Wrote {len(result['segmental'])} segmental units")
    if args.tonal_output:
        print(f"Wrote {len(result['tonal'])} tonal units")


if __name__ == "__main__":
    main()
