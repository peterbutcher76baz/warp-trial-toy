from collections import Counter
from string import punctuation


def _words(text: str) -> list[str]:
    words = (word.strip(punctuation) for word in text.split())
    return [word for word in words if word]


def word_count(text: str) -> int:
    return len(_words(text))


def mean_word_length(text: str) -> float:
    words = _words(text)
    if not words:
        return 0.0
    return sum(len(w) for w in words) / len(words)


def top_words(text: str, n: int) -> list[tuple[str, int]]:
    counts = Counter(w.lower() for w in _words(text))
    return counts.most_common(n)
