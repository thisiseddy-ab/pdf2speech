from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from .adapters.ffmpeg_audio_merger import FfmpegAudioMerger
from .domain.models import SpeechConfig
from .services.edge_tts_engine import EdgeTtsEngine
from .services.text_chunker import TextChunker
from .utils.files import ensure_empty_dir, ensure_parent_dir


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    speech = SpeechConfig(
        voice=args.voice,
        rate=args.rate,
        volume=args.volume,
        max_chars=args.max_chars,
    )
    tts = EdgeTtsEngine(config=speech)
    chunker = TextChunker(max_chars=speech.max_chars)
    merger = FfmpegAudioMerger()

    text_path = Path(args.text)
    out_path = Path(args.out)
    work_dir = out_path.parent / (out_path.stem + "_parts")

    text = text_path.read_text(encoding="utf-8")
    chunks = chunker.chunk(text)
    if not chunks:
        raise SystemExit("No text to synthesize.")

    ensure_parent_dir(out_path)
    ensure_empty_dir(work_dir)

    asyncio.run(_run(tts, merger, chunks, work_dir, out_path, keep_parts=args.keep_parts))
    return 0


async def _run(tts, merger, chunks, work_dir: Path, out_path: Path, keep_parts: bool) -> None:
    parts = []
    for i, chunk in enumerate(chunks, start=1):
        p = work_dir / f"part_{i:04d}.mp3"
        await tts.synthesize_to_file(chunk, p)
        parts.append(p)
    merger.merge(parts, out_path)
    if not keep_parts:
        # best-effort cleanup
        for p in parts:
            try:
                p.unlink()
            except FileNotFoundError:
                pass
        try:
            work_dir.rmdir()
        except OSError:
            pass
    print(f"OK: wrote {out_path}")


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="pdf2speech-text",
        description="Text file -> one MP3 via Edge TTS (uses syntok for sentence segmentation).",
    )
    p.add_argument("--text", required=True, help="Path to input .txt file (UTF-8).")
    p.add_argument("--out", required=True, help="Path to output MP3.")
    p.add_argument("--voice", default="en-US-ChristopherNeural", help="Edge TTS voice short name.")
    p.add_argument("--rate", default="+0%", help="Speech rate, e.g. '+0%', '-10%', '+15%'.")
    p.add_argument("--volume", default="+0%", help="Speech volume, e.g. '+0%', '-10%', '+10%'.")
    p.add_argument("--max-chars", type=int, default=3000, help="Max chars per TTS request.")
    p.add_argument("--keep-parts", action="store_true", help="Keep part_XXXX.mp3 files.")
    return p.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
