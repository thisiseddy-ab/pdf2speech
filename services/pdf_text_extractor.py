from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import fitz  # PyMuPDF


_PAGE_NUMBER_LINE_RE = re.compile(r"^\s*(?:page\s+)?(\d+|[ivxlcdm]+)\s*$", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class PdfTextExtractor:
    """Extract readable text from a PDF using PyMuPDF.

    Goal: reduce choppy TTS caused by PDF layout artifacts:
    - page headers/footers (title/author/page number) repeated every page
    - hard line wraps inside sentences

    Strategy:
    - extract text blocks in reading order (page.get_text("blocks"))
    - drop blocks located in top/bottom margins (header/footer)
    - remove standalone page-number lines as a second safety net
    """

    header_ratio: float = 0.07  # ignore top 7% of page height
    footer_ratio: float = 0.07  # ignore bottom 7% of page height

    def extract(self, pdf_path: Path) -> str:
        self._validate_path(pdf_path)
        doc = fitz.open(pdf_path)
        try:
            pages = [self._extract_page(page) for page in doc]
            # Join pages with a *single* newline so paragraph continuation can survive.
            # The chunker later unwraps single newlines inside paragraphs.
            return "\n".join(p for p in pages if p).strip()
        finally:
            doc.close()

    def _extract_page(self, page) -> str:
        rect = page.rect
        height = float(rect.height) if rect else 0.0
        header_y = height * self.header_ratio
        footer_y = height * (1.0 - self.footer_ratio)

        # blocks: (x0, y0, x1, y1, text, block_no, block_type)
        blocks = page.get_text("blocks") or []
        kept = []
        for b in blocks:
            x0, y0, x1, y1, text, *_ = b
            if height > 0:
                if y1 < header_y:
                    continue
                if y0 > footer_y:
                    continue
            txt = (text or "").strip()
            if not txt:
                continue
            kept.append((y0, x0, txt))

        kept.sort(key=lambda t: (t[0], t[1]))
        page_text = "\n".join(self._clean_lines(t[2]) for t in kept).strip()
        return page_text

    def _clean_lines(self, block_text: str) -> str:
        lines = []
        for ln in block_text.splitlines():
            s = ln.strip()
            if not s:
                continue
            if _PAGE_NUMBER_LINE_RE.match(s):
                continue
            lines.append(s)
        return "\n".join(lines).strip()

    @staticmethod
    def _validate_path(pdf_path: Path) -> None:
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        if pdf_path.suffix.lower() != ".pdf":
            raise ValueError(f"Not a PDF file: {pdf_path}")
