from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Sequence


@dataclass(frozen=True, slots=True)
class SpeechConfig:
    voice: str
    rate: str = "+0%"
    volume: str = "+0%"
    max_chars: int = 3000


@dataclass(frozen=True, slots=True)
class PdfToSpeechJob:
    pdf_path: Path
    out_audio_path: Path
    work_dir: Path
    keep_parts: bool = False


class TtsEngine(Protocol):
    async def synthesize_to_file(self, text: str, out_path: Path) -> None:
        ...

    async def list_voices(self) -> list[dict]:
        ...


class AudioMerger(Protocol):
    def merge(self, part_files: Sequence[Path], out_file: Path) -> None:
        ...
