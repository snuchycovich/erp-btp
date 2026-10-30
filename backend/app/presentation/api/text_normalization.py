"""Normalization helpers for untrusted plain-text API fields."""

from html.parser import HTMLParser

import nh3

_BLOCK_TAGS = frozenset(
    {
        "article",
        "blockquote",
        "div",
        "footer",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "header",
        "li",
        "ol",
        "p",
        "pre",
        "section",
        "table",
        "td",
        "th",
        "tr",
        "ul",
    }
)
_SEPARATOR_TAGS = _BLOCK_TAGS | {"br", "hr"}
_HTML_CLEANER = nh3.Cleaner(
    tags=_SEPARATOR_TAGS,
    clean_content_tags={"script", "style"},
    attributes={},
    strip_comments=True,
    link_rel=None,
)


class _PlainTextExtractor(HTMLParser):
    """Extract decoded text while preserving structural HTML boundaries."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Insert a separator before a structural element."""
        if tag in _SEPARATOR_TAGS:
            self._parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        """Insert a separator after a block element."""
        if tag in _BLOCK_TAGS:
            self._parts.append(" ")

    def handle_data(self, data: str) -> None:
        """Collect visible text from the sanitized fragment."""
        self._parts.append(data)

    def get_text(self) -> str:
        """Return decoded text with surrounding and repeated whitespace removed."""
        return " ".join("".join(self._parts).split())


def normalize_plain_text(value: str) -> str:
    """Convert untrusted HTML-like input into normalized plain text."""
    sanitized_html = _HTML_CLEANER.clean(value)
    extractor = _PlainTextExtractor()
    extractor.feed(sanitized_html)
    extractor.close()
    return extractor.get_text()
