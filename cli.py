from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from .adapters.ffmpeg_audio_merger import FfmpegAudioMerger
from .config import make_job
from .domain.models import SpeechConfig
from .services.edge_tts_engine import EdgeTtsEngine
from .services.pdf_text_extractor import PdfTextExtractor
from .services.pipeline import PdfToSpeechPipeline
from .services.text_chunker import TextChunker


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    if args.list_voices:
        return asyncio.run(_cmd_list_voices(locale_filter=args.locale))

    speech = SpeechConfig(
        voice=args.voice,
        rate=args.rate,
        volume=args.volume,
        max_chars=args.max_chars,
    )

    pipeline = PdfToSpeechPipeline(
        extractor=PdfTextExtractor(),
        chunker=TextChunker(max_chars=speech.max_chars),
        tts=EdgeTtsEngine(config=speech),
        merger=FfmpegAudioMerger(),
    )

    job = make_job(Path(args.pdf), Path(args.out), keep_parts=args.keep_parts)
    asyncio.run(_cmd_run(pipeline, job))
    return 0


async def _cmd_run(pipeline: PdfToSpeechPipeline, job) -> None:
    out = await pipeline.run(job)
    print(f"OK: wrote {out}")


async def _cmd_list_voices(locale_filter: str | None) -> int:
    # Use a dummy config just to access list_voices.
    engine = EdgeTtsEngine(config=SpeechConfig(voice="en-US-AriaNeural"))
    voices = await engine.list_voices()

    if locale_filter:
        voices = [v for v in voices if str(v.get("Locale", "")).startswith(locale_filter)]

    # Print a compact list
    for v in voices:
        short = v.get("ShortName", "")
        locale = v.get("Locale", "")
        gender = v.get("Gender", "")
        friendly = v.get("FriendlyName", "")
        print(f"{short} | {locale} | {gender} | {friendly}")
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="pdf2speech", description="Convert PDF to one MP3 via Edge TTS.")

    p.add_argument("--list-voices", action="store_true", help="List available Edge TTS voices and exit.")
    p.add_argument("--locale", default=None, help="Filter voices by locale prefix, e.g. 'de-' or 'en-US'.")

    p.add_argument("--pdf", help="Path to input PDF.")
    p.add_argument("--out", help="Path to output MP3.")
    p.add_argument("--voice", default="de-DE-KatjaNeural", help="Edge TTS voice short name.")
    p.add_argument("--rate", default="+0%", help="Speech rate, e.g. '+0%', '-10%', '+15%'.")
    p.add_argument("--volume", default="+0%", help="Speech volume, e.g. '+0%', '-10%', '+10%'.")
    p.add_argument("--max-chars", type=int, default=3000, help="Max chars per TTS request.")
    p.add_argument("--keep-parts", action="store_true", help="Keep generated part_XXXX.mp3 files.")

    args = p.parse_args(argv)

    if not args.list_voices:
        if not args.pdf or not args.out:
            p.error("--pdf and --out are required unless --list-voices is used.")

    return args
