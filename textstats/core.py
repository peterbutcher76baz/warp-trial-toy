from collections import Counter
from string import punctuation
from unicodedata import category


def _is_punctuation(character: str) -> bool:
    return character in punctuation or category(character).startswith("P")


def _words(text: str) -> list[str]:
    words = []
    for word in text.split():
        start, end = 0, len(word)
        while start < end and _is_punctuation(word[start]):
            start += 1
        while end > start and _is_punctuation(word[end - 1]):
            end -= 1
        if start < end:
            words.append(word[start:end])
    return words


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
