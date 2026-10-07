#!/usr/bin/env bash

set -euo pipefail

python -m crossphon.phone_mapping \
  examples/cantonese_to_english/cantonese.txt \
  examples/cantonese_to_english/english_ipas.txt \
  example_outputs/cantonese_to_english/phone_mapping.txt

python -m crossphon.tonal_mapping \
  examples/cantonese_to_english/cantonese_tonal.txt \
  examples/cantonese_to_english/english_ipas.txt \
  example_outputs/cantonese_to_english/phone_mapping.txt \
  example_outputs/cantonese_to_english/final_mapping.txt

python -m crossphon.intermediate_dictionary \
  examples/cantonese_to_english/sample_source.dict \
  example_outputs/cantonese_to_english/final_mapping.txt \
  example_outputs/cantonese_to_english/intermediate_dictionary.dict

python -m crossphon.phone_mapping \
  examples/mandarin_to_vietnamese/mandarin.txt \
  examples/mandarin_to_vietnamese/vietnamese.txt \
  example_outputs/mandarin_to_vietnamese/phone_mapping.txt

python -m crossphon.tonal_mapping \
  examples/mandarin_to_vietnamese/mandarin_tonal.txt \
  examples/mandarin_to_vietnamese/vietnamese_tonal.txt \
  example_outputs/mandarin_to_vietnamese/phone_mapping.txt \
  example_outputs/mandarin_to_vietnamese/final_mapping.txt

python -m crossphon.intermediate_dictionary \
  examples/mandarin_to_vietnamese/sample_source.dict \
  example_outputs/mandarin_to_vietnamese/final_mapping.txt \
  example_outputs/mandarin_to_vietnamese/intermediate_dictionary.dict

echo "Examples completed. Results are in example_outputs/."
