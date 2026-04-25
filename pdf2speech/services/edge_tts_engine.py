from __future__ import annotations

import asyncio
import random
import socket
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from pathlib import Path
from typing import TypeVar

import aiohttp
import edge_tts

from ..domain.models import SpeechConfig, TtsEngine

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class EdgeTtsRetryPolicy:
    max_attempts: int = 5
    initial_delay_seconds: float = 2.0
    max_delay_seconds: float = 30.0
    backoff_multiplier: float = 2.0
    jitter_seconds: float = 0.5

    def delay_for_attempt(self, attempt: int) -> float:
        """Return the delay before the next retry.

        attempt is 1-based and represents the failed attempt number.
        """
        base_delay = self.initial_delay_seconds * (self.backoff_multiplier ** max(attempt - 1, 0))
        capped_delay = min(base_delay, self.max_delay_seconds)
        if self.jitter_seconds <= 0:
            return capped_delay
        return capped_delay + random.uniform(0.0, self.jitter_seconds)


_RETRYABLE_EDGE_TTS_ERRORS: tuple[type[BaseException], ...] = (
    aiohttp.ClientError,
    asyncio.TimeoutError,
    socket.gaierror,
)


@dataclass(frozen=True, slots=True)
class EdgeTtsEngine(TtsEngine):
    config: SpeechConfig
    retry_policy: EdgeTtsRetryPolicy = EdgeTtsRetryPolicy()

    async def synthesize_to_file(self, text: str, out_path: Path) -> None:
        async def synthesize_once() -> None:
            # Create a fresh Communicate object on every attempt. If the websocket
            # or DNS lookup failed, reusing the old object can keep stale state.
            communicate = edge_tts.Communicate(
                text=text,
                voice=self.config.voice,
                rate=self.config.rate,
                volume=self.config.volume,
            )
            await communicate.save(str(out_path))

        await self._run_with_retries(
            operation=synthesize_once,
            operation_name=f"TTS synthesis for {out_path.name}",
            cleanup=lambda: self._safe_unlink(out_path),
        )

    async def list_voices(self) -> list[dict]:
        return await self._run_with_retries(
            operation=edge_tts.list_voices,
            operation_name="Edge TTS voice list",
        )

    async def _run_with_retries(
        self,
        operation: Callable[[], Awaitable[T]],
        operation_name: str,
        cleanup: Callable[[], None] | None = None,
    ) -> T:
        last_error: BaseException | None = None

        for attempt in range(1, self.retry_policy.max_attempts + 1):
            try:
                return await operation()
            except _RETRYABLE_EDGE_TTS_ERRORS as error:
                last_error = error

                if cleanup is not None:
                    cleanup()

                if attempt >= self.retry_policy.max_attempts:
                    break

                delay = self.retry_policy.delay_for_attempt(attempt)
                print(
                    f"[Edge TTS retry] {operation_name} failed with "
                    f"{error.__class__.__name__}: {error}. "
                    f"Attempt {attempt}/{self.retry_policy.max_attempts}. "
                    f"Retrying in {delay:.1f}s..."
                )
                await asyncio.sleep(delay)

        raise RuntimeError(
            f"{operation_name} failed after {self.retry_policy.max_attempts} attempts."
        ) from last_error

    @staticmethod
    def _safe_unlink(path: Path) -> None:
        try:
            path.unlink(missing_ok=True)
        except OSError:
            return
