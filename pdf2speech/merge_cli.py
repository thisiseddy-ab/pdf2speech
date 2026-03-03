from __future__ import annotations

import argparse
from pathlib import Path

from .adapters.ffmpeg_audio_merger import FfmpegAudioMerger


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    parts_dir = Path(args.parts_dir)
    out_file = Path(args.out)

    part_files = _collect_parts(parts_dir, pattern=args.pattern)
    if not part_files:
        raise SystemExit(f"No part files found in: {parts_dir} (pattern: {args.pattern})")

    out_file.parent.mkdir(parents=True, exist_ok=True)
    merger = FfmpegAudioMerger(ffmpeg_cmd=args.ffmpeg)
    merger.merge(part_files, out_file)

    print(f"OK: merged {len(part_files)} parts -> {out_file}")
    return 0


def _collect_parts(parts_dir: Path, pattern: str) -> list[Path]:
    if not parts_dir.exists():
        raise SystemExit(f"Parts directory does not exist: {parts_dir}")
    if not parts_dir.is_dir():
        raise SystemExit(f"Not a directory: {parts_dir}")

    # Sort by filename so part_0001.mp3 ... part_9999.mp3 are in the right order.
    return sorted(parts_dir.glob(pattern), key=lambda p: p.name)


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="pdf2speech-merge",
        description="Merge existing part_XXXX.mp3 files into one MP3 using ffmpeg (no re-synthesis).",
    )
    p.add_argument("--parts-dir", required=True, help="Directory containing part_XXXX.mp3 files.")
    p.add_argument("--out", required=True, help="Output MP3 file path.")
    p.add_argument(
        "--pattern",
        default="part_*.mp3",
        help="Glob pattern for parts inside --parts-dir (default: part_*.mp3).",
    )
    p.add_argument(
        "--ffmpeg",
        default="ffmpeg",
        help="ffmpeg command name or full path (default: ffmpeg).",
    )
    return p.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
