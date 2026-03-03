from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..domain.models import AudioMerger, PdfToSpeechJob, TtsEngine
from ..utils.files import ensure_empty_dir, ensure_parent_dir, safe_unlink
from .pdf_text_extractor import PdfTextExtractor
from .text_chunker import TextChunker


@dataclass(frozen=True, slots=True)
class PdfToSpeechPipeline:
    extractor: PdfTextExtractor
    chunker: TextChunker
    tts: TtsEngine
    merger: AudioMerger

    async def run(self, job: PdfToSpeechJob) -> Path:
        ensure_parent_dir(job.out_audio_path)
        ensure_empty_dir(job.work_dir)

        extracted = self.extractor.extract(job.pdf_path)
        if not extracted.strip():
            raise ValueError("No text extracted from PDF. Is it a scanned PDF?")

        extracted_path = job.out_audio_path.with_suffix(job.out_audio_path.suffix + ".extracted.txt")
        extracted_path.write_text(extracted, encoding="utf-8")

        chunks = self.chunker.chunk(extracted)
        normalized_path = job.out_audio_path.with_suffix(job.out_audio_path.suffix + ".normalized.txt")
        normalized_path.write_text("\n\n".join(chunks), encoding="utf-8")

        part_files = await self._synthesize_parts(chunks, job.work_dir)
        self.merger.merge(part_files, job.out_audio_path)

        if not job.keep_parts:
            self._cleanup(job.work_dir, part_files)

        return job.out_audio_path

    async def _synthesize_parts(self, chunks: list[str], work_dir: Path) -> list[Path]:
        part_files: list[Path] = []
        for i, chunk in enumerate(chunks, start=1):
            part_path = work_dir / f"part_{i:04d}.mp3"
            await self.tts.synthesize_to_file(chunk, part_path)
            part_files.append(part_path)
        return part_files

    def _cleanup(self, work_dir: Path, part_files: list[Path]) -> None:
        for f in part_files:
            safe_unlink(f)
        try:
            work_dir.rmdir()
        except OSError:
            return
