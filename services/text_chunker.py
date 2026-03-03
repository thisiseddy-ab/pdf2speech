from __future__ import annotations

import re
from dataclasses import dataclass

import syntok.segmenter as segmenter


_LIST_ITEM_RE = re.compile(r"^\s*(?:[-•*]|\d+[\.)])\s+")


@dataclass(frozen=True, slots=True)
class TextChunker:
    """Chunk text for TTS with natural boundaries (CPU-only).

    Fixes the main "choppiness" issues from PDFs:
    1) Hard line wraps inside a paragraph (newline mid-sentence) -> unwrap into spaces
    2) Hyphenation across line breaks: "hyphen-\nated" -> "hyphenated"
    3) Chunk splitting uses **syntok** sentence segmentation instead of naive char splitting,
       so TTS chunks end on natural sentence boundaries.

    Notes:
    - Paragraph breaks are kept as blank lines (\n\n) to preserve natural pauses.
    - Bullet/numbered lists keep line structure.
    """

    max_chars: int

    def chunk(self, text: str) -> list[str]:
        cleaned = self._normalize(text)
        paragraphs = self._split_paragraphs(cleaned)
        return self._pack(paragraphs)

    def _normalize(self, text: str) -> str:
        # Normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Collapse repeated spaces; keep newlines for paragraph detection
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"[ \t]+\n", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Join hyphenated word-breaks across a newline if next char is lowercase
        text = re.sub(r"(?<=\w)-\n(?=[a-zà-ž])", "", text)

        # Unwrap single newlines inside paragraphs (common PDF line wrapping).
        paragraphs = self._split_paragraphs(text)
        unwrapped = [self._unwrap_lines(p) for p in paragraphs]
        return "\n\n".join(p for p in unwrapped if p).strip()

    def _unwrap_lines(self, paragraph: str) -> str:
        lines = [ln.strip() for ln in paragraph.split("\n") if ln.strip()]
        if len(lines) <= 1:
            return paragraph.strip()

        # Keep line breaks for list-like paragraphs
        list_like = sum(1 for ln in lines if _LIST_ITEM_RE.match(ln))
        if list_like >= max(2, int(0.6 * len(lines))):
            return "\n".join(lines).strip()

        return re.sub(r"\s{2,}", " ", " ".join(lines)).strip()

    def _split_paragraphs(self, text: str) -> list[str]:
        parts = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        return parts if parts else [text] if text else []

    def _pack(self, paragraphs: list[str]) -> list[str]:
        chunks: list[str] = []
        buf = ""
        for p in paragraphs:
            if not buf:
                buf = p
                continue

            candidate = f"{buf}\n\n{p}"
            if len(candidate) <= self.max_chars:
                buf = candidate
                continue

            chunks.extend(self._split_big_block(buf))
            buf = p

        if buf:
            chunks.extend(self._split_big_block(buf))

        return [c for c in (c.strip() for c in chunks) if c]

    def _split_big_block(self, block: str) -> list[str]:
        if len(block) <= self.max_chars:
            return [block]

        # Split block into paragraphs first so we keep \n\n pauses where present.
        paras = self._split_paragraphs(block)
        out: list[str] = []
        for para in paras:
            if len(para) <= self.max_chars:
                out.append(para)
            else:
                out.extend(self._split_by_sentences(para))
        return self._pack_small(out)

    def _split_by_sentences(self, text: str) -> list[str]:
        sents = self._syntok_sentences(text)
        if not sents:
            return self._hard_split_chars(text)

        # Pack sentences into chunks
        packed: list[str] = []
        buf = ""
        for s in sents:
            if not buf:
                buf = s
                continue

            candidate = f"{buf} {s}"
            if len(candidate) <= self.max_chars:
                buf = candidate
                continue

            packed.append(buf)
            buf = s

        if buf:
            packed.append(buf)

        # If any sentence is still too long, fallback to char splitting
        final: list[str] = []
        for p in packed:
            if len(p) <= self.max_chars:
                final.append(p)
            else:
                final.extend(self._hard_split_chars(p))
        return final

    def _syntok_sentences(self, text: str) -> list[str]:
        sentences: list[str] = []
        for paragraph in segmenter.analyze(text):
            for sentence in paragraph:
                # Preserve original spacing as much as possible
                s = "".join(tok.spacing + tok.value for tok in sentence).strip()
                if s:
                    sentences.append(s)
        return sentences

    def _hard_split_chars(self, text: str) -> list[str]:
        out: list[str] = []
        start = 0
        while start < len(text):
            end = min(start + self.max_chars, len(text))
            out.append(text[start:end].strip())
            start = end
        return [c for c in out if c]

    def _pack_small(self, blocks: list[str]) -> list[str]:
        # After splitting, try to repack small blocks into max_chars chunks again.
        out: list[str] = []
        buf = ""
        for b in blocks:
            if not buf:
                buf = b
                continue
            candidate = f"{buf}\n\n{b}"
            if len(candidate) <= self.max_chars:
                buf = candidate
            else:
                out.append(buf)
                buf = b
        if buf:
            out.append(buf)
        return out
