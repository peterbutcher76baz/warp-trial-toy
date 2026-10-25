from collections import Counter


def _words(text: str) -> list[str]:
    return text.split()


def word_count(text: str) -> int:
    return len(_words(text))


def mean_word_length(text: str) -> float:
    words = _words(text)
    return sum(len(w) for w in words) / len(words)


def top_words(text: str, n: int) -> list[tuple[str, int]]:
    counts = Counter(w.lower() for w in _words(text))
    return counts.most_common(n)
