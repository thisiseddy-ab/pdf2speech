from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .domain.models import PdfToSpeechJob, SpeechConfig


@dataclass(frozen=True, slots=True)
class AppConfig:
    speech: SpeechConfig


def default_work_dir(out_audio_path: Path) -> Path:
    return out_audio_path.parent / (out_audio_path.stem + "_parts")


def make_job(pdf_path: Path, out_audio_path: Path, keep_parts: bool) -> PdfToSpeechJob:
    return PdfToSpeechJob(
        pdf_path=pdf_path,
        out_audio_path=out_audio_path,
        work_dir=default_work_dir(out_audio_path),
        keep_parts=keep_parts,
    )
