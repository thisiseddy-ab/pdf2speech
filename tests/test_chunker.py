from pdf2speech.services.text_chunker import TextChunker


def test_unwraps_hard_line_breaks():
    chunker = TextChunker(max_chars=10_000)
    raw = "The place was cozy, with floral patterns, overstuffed\nfurniture, and—literally—a fence."
    chunks = chunker.chunk(raw)
    assert len(chunks) == 1
    assert "overstuffed furniture" in chunks[0]


def test_dehyphenates_line_breaks():
    chunker = TextChunker(max_chars=10_000)
    raw = "This is hyphen-\nated text."
    chunks = chunker.chunk(raw)
    assert "hyphenated" in chunks[0]


def test_sentence_aware_splitting():
    chunker = TextChunker(max_chars=25)
    raw = "First sentence. Second sentence! Third sentence?"
    chunks = chunker.chunk(raw)
    assert all(len(c) <= 25 for c in chunks)
