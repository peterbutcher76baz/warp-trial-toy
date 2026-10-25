# textstats

A tiny Python library for simple text statistics.

## Use

```python
from textstats import word_count, mean_word_length, top_words

word_count("The cat sat on the mat")        # 6
mean_word_length("The cat sat")             # 3.0
top_words("the cat and the hat", 1)         # [("the", 2)]
```

All functions split words on whitespace, strip ASCII punctuation from each word's
edges, and ignore tokens that become empty. Punctuation inside a word stays
unchanged, including apostrophes and hyphens.

## Test

```bash
pip install -r requirements.txt
pytest
```
