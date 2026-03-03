from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import edge_tts

from ..domain.models import SpeechConfig, TtsEngine


@dataclass(frozen=True, slots=True)
class EdgeTtsEngine(TtsEngine):
    config: SpeechConfig

    async def synthesize_to_file(self, text: str, out_path: Path) -> None:
        communicate = edge_tts.Communicate(
            text=text,
            voice=self.config.voice,
            rate=self.config.rate,
            volume=self.config.volume,
        )
        await communicate.save(str(out_path))

    async def list_voices(self) -> list[dict]:
        return await edge_tts.list_voices()
