https://huggingface.co/spaces/innoai/Edge-TTS-Text-to-Speech

How to use (after unzip)
pip install -r requirements.txt

Convert PDF → one MP3:

python -m pdf2speech --pdf "input.pdf" --out "output.mp3" --voice "de-DE-KatjaNeural"

List voices:

python -m pdf2speech --list-voices --locale en-

Keep the intermediate part_XXXX.mp3 files:

python -m pdf2speech --pdf input.pdf --out output.mp3 --keep-parts
Note (merging)

The project merges to one file using ffmpeg. Make sure ffmpeg is installed and on your PATH:

ffmpeg -version

Option A (easiest): winget (Windows 10/11)

Open PowerShell (or Windows Terminal)

Run:

winget install --id Gyan.FFmpeg

Close and reopen your terminal, then verify:

ffmpeg -version


my setting :
python -m pdf2speech --pdf "input.pdf" --out "output.mp3" --voice "en-US-ChristopherNeural" --keep-parts

python -m pdf2speech.merge_cli --parts-dir "output_parts" --out "book.mp3"
