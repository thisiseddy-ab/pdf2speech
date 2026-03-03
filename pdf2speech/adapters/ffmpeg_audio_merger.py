from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from ..domain.models import AudioMerger
from ..utils.proc import which


@dataclass(frozen=True, slots=True)
class FfmpegAudioMerger(AudioMerger):
    """Merge MP3 parts into one MP3 using ffmpeg concat demuxer (lossless)."""

    ffmpeg_cmd: str = "ffmpeg"

    def merge(self, part_files: Sequence[Path], out_file: Path) -> None:
        if not part_files:
            raise ValueError("No audio parts to merge.")
        if which(self.ffmpeg_cmd) is None:
            raise RuntimeError(
                "ffmpeg not found on PATH. Install ffmpeg to merge MP3 parts into one file."
            )

        concat_file = out_file.parent / (out_file.stem + "_concat.txt")
        concat_file.write_text(self._concat_manifest(part_files), encoding="utf-8")

        try:
            self._run_ffmpeg(concat_file, out_file)
        finally:
            # Best-effort cleanup of manifest
            try:
                concat_file.unlink()
            except FileNotFoundError:
                pass

    def _run_ffmpeg(self, concat_file: Path, out_file: Path) -> None:
        cmd = [
            self.ffmpeg_cmd,
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            str(out_file),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(
                "ffmpeg merge failed.\n"
                f"Command: {' '.join(cmd)}\n"
                f"STDOUT: {proc.stdout}\n"
                f"STDERR: {proc.stderr}"
            )

    def _concat_manifest(self, part_files: Sequence[Path]) -> str:
        # ffmpeg concat wants:
        # file 'path/to/part_0001.mp3'
        lines = []
        for p in part_files:
            # Use forward slashes for better cross-platform behavior
            path_str = str(p).replace("\\", "/")
            lines.append(f"file '{path_str}'")
        return "\n".join(lines) + "\n"
