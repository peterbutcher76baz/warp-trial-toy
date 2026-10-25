from textstats import mean_word_length, top_words, word_count


def test_word_count():
    assert word_count("The cat sat on the mat") == 6


def test_word_count_empty():
    assert word_count("") == 0


def test_mean_word_length():
    assert mean_word_length("The cat sat") == 3.0


def test_top_words():
    assert top_words("the cat and the hat", 1) == [("the", 2)]


def test_top_words_ignores_case():
    assert top_words("The the THE cat", 1) == [("the", 3)]
