from textstats import mean_word_length, top_words, word_count


def test_word_count():
    assert word_count("The cat sat on the mat") == 6


def test_word_count_empty():
    assert word_count("") == 0


def test_mean_word_length():
    assert mean_word_length("The cat sat") == 3.0


def test_mean_word_length_empty():
    assert mean_word_length("") == 0.0


def test_mean_word_length_whitespace():
    assert mean_word_length(" \t\n ") == 0.0


def test_top_words():
    assert top_words("the cat and the hat", 1) == [("the", 2)]


def test_top_words_ignores_case():
    assert top_words("The the THE cat", 1) == [("the", 3)]


def test_top_words_combines_punctuated_words():
    assert top_words("cat. cat", 2) == [("cat", 2)]


def test_statistics_strip_edge_punctuation():
    text = "...((CaT!!))\t!!!\n--cat?? longer..."
    assert word_count(text) == 3
    assert mean_word_length(text) == 4.0
    assert top_words(text, 2) == [("cat", 2), ("longer", 1)]


def test_statistics_ignore_punctuation_only_input():
    text = "!!! ... --"
    assert word_count(text) == 0
    assert mean_word_length(text) == 0.0
    assert top_words(text, 2) == []


def test_statistics_preserve_internal_punctuation():
    text = "don't re-enter don't"
    assert word_count(text) == 3
    assert mean_word_length(text) == 6.0
    assert top_words(text, 2) == [("don't", 2), ("re-enter", 1)]
