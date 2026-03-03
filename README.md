# pdf2speech-clean

A small **Clean Code / SOLID** Python project that converts a PDF to **one** audio file:

1) Extract text from PDF (PyMuPDF)
2) Chunk text into safe sizes
3) Synthesize each chunk with Edge Neural TTS (edge-tts)
4) Merge the chunk MP3s into a single MP3 using **ffmpeg concat**

## Why this is “clean” / SOLID

- **Single Responsibility**: text extraction, chunking, TTS, and merging are separate services.
- **Open/Closed**: you can add a new TTS engine (Azure/OpenAI/etc.) by implementing `TtsEngine`.
- **Liskov**: engines/mergers follow the same contracts.
- **Interface Segregation**: small focused interfaces (`TtsEngine`, `AudioMerger`).
- **Dependency Inversion**: pipeline depends on abstractions, not concrete implementations.

---

## Install

```bash
pip install -r requirements.txt
```

### ffmpeg requirement (for merging)
The default merger uses `ffmpeg` for a fast, lossless concat of MP3 parts.

- Windows: install ffmpeg and ensure it is on PATH
- macOS: `brew install ffmpeg`
- Linux: `sudo apt-get install ffmpeg` (or equivalent)

Check:
```bash
ffmpeg -version
```

---

## Usage

Convert a PDF into a single MP3:

```bash
python -m pdf2speech --pdf "input.pdf" --out "output.mp3" --voice "de-DE-KatjaNeural"
```

List voices (filter by locale if you want):

```bash
python -m pdf2speech --list-voices --locale de-
```

Keep temporary part files (useful for debugging):

```bash
python -m pdf2speech --pdf input.pdf --out out.mp3 --keep-parts
```

Customize chunk size (if you hit service limits):

```bash
python -m pdf2speech --pdf input.pdf --out out.mp3 --max-chars 2800
```

---


### Merge-only (if synthesis already finished but merging failed)

If you already have the `part_XXXX.mp3` files, you can merge them into one MP3 without running TTS again:

```bash
python -m pdf2speech.merge_cli --parts-dir "output_parts_folder" --out "output.mp3"
```

Example: if your output is `book.mp3`, the default parts folder is `book_parts/` (next to the output):

```bash
python -m pdf2speech.merge_cli --parts-dir "book_parts" --out "book.mp3"
```


## Choppy voice fixes (PDF line wraps + sentence-aware chunking)

This project uses **syntok** for CPU-only sentence segmentation, so chunk splits happen at
natural sentence boundaries (instead of cutting mid-sentence). It also unwraps hard PDF
line breaks and joins hyphenated word breaks.

Install syntok:

```bash
pip install syntok
```

### Re-run from extracted text (no PDF re-extraction)

The PDF pipeline writes:
- `output.mp3.extracted.txt`
- `output.mp3.normalized.txt`

You can edit `*.extracted.txt` (remove headers, fix weird breaks) and then run:

```bash
python -m pdf2speech.text_cli --text "output.mp3.extracted.txt" --out "output.mp3"
```

## Notes

- This works best for **text-based PDFs**. If the PDF is **scanned images**, you need OCR first.
- Edge TTS is an online service, so you need internet.

---

## Project layout

```
pdf2speech/
  domain/         # dataclasses, interfaces
  services/       # business logic
  adapters/       # ffmpeg merger adapter
  utils/          # small helpers
  cli.py          # wiring (composition root)
```
