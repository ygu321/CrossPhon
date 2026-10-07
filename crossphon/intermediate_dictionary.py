"""Convert a pronunciation dictionary with a CrossPhon phone mapping."""

import argparse


def load_phone_mapping(mapping_file):
    """Load the phone mapping from file."""
    phone_mapping = {}
    with open(mapping_file, "r", encoding="utf-8") as file:
        for line in file:
            source, target = line.strip().split("\t")
            phone_mapping[source] = target
    return phone_mapping


def convert_ipa(ipa, phone_mapping):
    """Convert IPA symbols based on the mapping."""
    return phone_mapping.get(ipa, ipa)


def process_dictionary(input_file, output_file, phone_mapping):
    """Process the dictionary file."""
    with open(input_file, "r", encoding="utf-8") as infile, open(
        output_file, "w", encoding="utf-8"
    ) as outfile:
        for line in infile:
            elements = line.strip().split("\t")
            vocabulary = elements[0]
            pronunciation = elements[-1]
            ipas = pronunciation.split()
            converted_ipas = [convert_ipa(ipa, phone_mapping) for ipa in ipas]
            converted_pronunciation = " ".join(converted_ipas)
            elements[-1] = converted_pronunciation
            outfile.write("\t".join(elements) + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Apply a CrossPhon mapping to a pronunciation dictionary."
    )
    parser.add_argument("dictionary", help="Source pronunciation dictionary")
    parser.add_argument("mapping", help="Tab-separated phone mapping")
    parser.add_argument("output", help="Output intermediate dictionary")
    args = parser.parse_args()

    phone_mapping = load_phone_mapping(args.mapping)
    process_dictionary(args.dictionary, args.output, phone_mapping)
    print(f"Conversion complete. Output written to '{args.output}'")


if __name__ == "__main__":
    main()
