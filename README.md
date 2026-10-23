# CrossPhon and CrossPhon-Tonal
**Automatic IPA phone and tone mapping for cross-language forced alignment.**

**CrossPhon** is an open-source Python tool for automatically mapping IPA phones between languages using articulatory phonetic features. It helps researchers perform cross-language forced alignment when language-specific acoustic models are unavailable, particularly for low-resource languages.

**CrossPhon-Tonal** extends the framework with automatic lexical tone mapping, enabling cross-language forced alignment between tonal and non-tonal languages.

The toolkit supports automatic phone inventory extraction, phonetic distance-based mapping, tone mapping, and pronunciation dictionary conversion.
- [CrossPhon: An Auto Phone Mapping Tool to Streamline Cross-language Modeling for Phone Alignment of Low-resource Languages](https://doi.org/10.21437/Interspeech.2025-2401), Interspeech 2025
- [CrossPhon-Tonal: Streamlining Cross-language Modeling for Forced Alignment in Low-resource Tonal Languages](https://www.isca-archive.org/interspeech_2026/wu26e_interspeech.html), Interspeech 2026

CrossPhon converts a source-language pronunciation dictionary so it can be used with an acoustic model trained for a target language. CrossPhon-Tonal extends the workflow to languages written with Chao tone letters (`˩ ˨ ˧ ˦ ˥`).

## Usage

### Install

Download or clone this repository, open a terminal in its folder, and run:

```bash
pip install .
```

Python 3.9 or newer is required. No third-party Python packages are needed.

### Prepare the dictionaries

You need:

- `source.dict`: the dictionary for the language in your recordings
- `target.dict`: the dictionary used by the target acoustic model

The files must be UTF-8 text. Put one word on each line, a tab after the word, and spaces between IPA phones:

```text
example	ɪ ɡ z æ m p əl
word	w ɝ d
```

### Create the phone inventories and basic mapping

Run these commands for all four situations described below:

```bash
python -m crossphon.inventory source.dict source_phones.txt --tonal-output source_full_phones.txt
python -m crossphon.inventory target.dict target_phones.txt --tonal-output target_full_phones.txt
python -m crossphon.phone_mapping source_phones.txt target_phones.txt phone_mapping.txt
```

Open `phone_mapping.txt` and check the suggested phone pairs before continuing.

### Choose your situation

The **source** is the language in your recordings. The **target** is the language of the acoustic model.

| Situation | What CrossPhon does |
| --- | --- |
| Tonal → tonal | Maps source phones and tones to forms supported by the tonal target model. |
| Tonal → non-tonal | Maps the phones and removes tones when the target supports only a non-tonal form. |
| Non-tonal → non-tonal | Maps phones only; no tone-processing step is needed. |
| Non-tonal → tonal | Prefers a target phone without tone; if none exists, selects a supported target tone. |

#### Tonal source → tonal target

```bash
python -m crossphon.tonal_mapping source_full_phones.txt target_full_phones.txt phone_mapping.txt final_mapping.txt
python -m crossphon.intermediate_dictionary source.dict final_mapping.txt intermediate_dictionary.dict
```

#### Tonal source → non-tonal target

```bash
python -m crossphon.tonal_mapping source_full_phones.txt target_full_phones.txt phone_mapping.txt final_mapping.txt
python -m crossphon.intermediate_dictionary source.dict final_mapping.txt intermediate_dictionary.dict
```

#### Non-tonal source → non-tonal target

```bash
python -m crossphon.intermediate_dictionary source.dict phone_mapping.txt intermediate_dictionary.dict
```

#### Non-tonal source → tonal target

```bash
python -m crossphon.tonal_mapping source_full_phones.txt target_full_phones.txt phone_mapping.txt final_mapping.txt
python -m crossphon.intermediate_dictionary source.dict final_mapping.txt intermediate_dictionary.dict
```

The result is `intermediate_dictionary.dict`. Phones absent from the mapping are kept unchanged. Review the finished mapping and test it on a small audio sample before aligning a complete corpus.

## Examples

- `examples/cantonese_to_english`: tonal source → non-tonal target
- `examples/mandarin_to_vietnamese`: tonal source → tonal target

To run both examples from the repository folder:

```bash
bash run_examples.sh
```

The generated mappings and intermediate dictionaries will be saved in `example_outputs/`. The small `sample_source.dict` files show the expected dictionary format and can be edited to try other words.

## Repository structure

```text
crossphon/   Phone inventory, phone mapping, tone mapping, and dictionary scripts
examples/    Sample inventories and mappings
tests/       Reproducibility tests
LICENSE      MIT License
```

## Citation

If you use CrossPhon, please cite:

```bibtex
@inproceedings{wu25l_interspeech,
  title     = {{CrossPhon: An Auto Phone Mapping Tool to Streamline Cross-language Modeling for Phone Alignment of Low-resource Languages}},
  author    = {Hongchen Wu and Yixin Gu},
  year      = {2025},
  booktitle = {{Interspeech 2025}},
  pages     = {86--90},
  doi       = {10.21437/Interspeech.2025-2401}
}
```

For tone mapping, please also cite:

```bibtex
@inproceedings{wu26e_interspeech,
  title     = {{CrossPhon-Tonal: Streamlining Cross-language Modeling for Forced Alignment in Low-resource Tonal Languages}},
  author    = {Hongchen Wu and Yixin Gu},
  year      = {2026},
  booktitle = {{Interspeech 2026}},
  pages     = {2135--2139},
  doi       = {10.21437/Interspeech.2026-1770}
}
```

## License

This project is released under the [MIT License](LICENSE).

## Contact Info
hwu480 at gatech dot edu

yixingu2 at illinois dot edu
