import re

_STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with", "is", "are",
    "this", "that", "by", "as", "at", "it", "its", "from", "you", "your", "yours",
    "their", "they", "she", "her", "he", "his", "we", "our",
    "recent", "recently", "article", "articles", "topic", "topics", "coverage",
    "reporting", "writing", "work", "given", "interest", "regularly", "often",
    "frequently", "cover", "covers", "covering", "about", "regarding",
}

_WORD_PATTERN = re.compile(r"[a-zA-Z]+")

# Claim patterns are deliberately anchored to second-person phrasing ("you"/"your"),
# since a pitch is addressed directly to the journalist. This avoids false positives
# on unrelated campaign/product language elsewhere in the same text.
_COVERAGE_CLAIM_PATTERNS = [
    re.compile(
        r"your (?:\w+ )?(?:coverage|reporting|writing|articles?|work) "
        r"(?:on|about|regarding|of|in) ([a-zA-Z][a-zA-Z \-]{1,60}?)(?=[.,;\n]|$)",
        re.IGNORECASE,
    ),
    re.compile(
        r"\byou(?:r)? (?:regularly |often |frequently |consistently )?"
        r"(?:cover|covers|write about|writes about|report on|reports on|focus on|focuses on) "
        r"([a-zA-Z][a-zA-Z \-]{1,60}?)(?=[.,;\n]|$)",
        re.IGNORECASE,
    ),
    re.compile(
        r"given your interest in ([a-zA-Z][a-zA-Z \-]{1,60}?)(?=[.,;\n]|$)",
        re.IGNORECASE,
    ),
]


def tokenize(text: str) -> set[str]:
    """Extract meaningful (non-stopword) lowercase word tokens from free text."""
    return {word for word in _WORD_PATTERN.findall(text.lower()) if len(word) >= 2 and word not in _STOPWORDS}


def build_vocabulary(*texts: str) -> set[str]:
    """Build the set of known tokens from the journalist's actual source information."""
    vocabulary: set[str] = set()
    for text in texts:
        vocabulary |= tokenize(text)
    return vocabulary


def find_ungrounded_items(items: list[str], vocabulary: set[str]) -> list[str]:
    """Return the items that share no meaningful token overlap with the known vocabulary.

    An item with no meaningful tokens of its own (e.g. punctuation-only) is not flagged,
    since there is nothing concrete in it to verify.
    """
    ungrounded = []
    for item in items:
        tokens = tokenize(item)
        if tokens and vocabulary.isdisjoint(tokens):
            ungrounded.append(item)
    return ungrounded


def extract_journalist_coverage_claims(text: str) -> list[str]:
    """Extract phrases that assert what topics the journalist personally covers or is interested in."""
    claims = []
    for pattern in _COVERAGE_CLAIM_PATTERNS:
        claims.extend(match.group(1).strip() for match in pattern.finditer(text))
    return claims
