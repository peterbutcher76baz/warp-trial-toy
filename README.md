# textstats

A tiny Python library for simple text statistics.

## Use

```python
from textstats import word_count, mean_word_length, top_words

word_count("The cat sat on the mat")        # 6
mean_word_length("The cat sat")             # 3.0
top_words("the cat and the hat", 1)         # [("the", 2)]
```

All functions split words on whitespace and strip Unicode punctuation from each
word's edges. ASCII characters in `string.punctuation`, including symbols such as
`$` and `+`, are also stripped. Tokens that become empty are ignored. Punctuation
inside a word stays unchanged, including apostrophes and hyphens.

## Command line

Requires Python 3.12 or later. Install from this checkout:

```bash
python -m pip install .
```

Run the installed command or the equivalent module:

```bash
textstats essay.txt
python -m textstats --json --top 3 "draft essay.txt"
```

Usage: `textstats [-h] [--top N] [--json] FILE`.

- `FILE` is one UTF-8 text file. An initial UTF-8 BOM is stripped; invalid UTF-8
  is rejected. Paths are relative to the working directory unless absolute.
- `--top N` limits the top-word entries (default `10`). Use nonnegative decimal
  digits; `0` omits entries. Repeated options use the last value.
- `--json` prints one JSON object with `word_count`, `mean_word_length`, and an
  ordered `top_words` array of `{"word": "...", "count": 1}` objects. It preserves
  full mean precision and escapes non-ASCII characters.
- `-h` or `--help` prints help without reading a file.

For a file containing `The cat sat on the mat`, the default report is:

```text
word_count: 6
mean_word_length: 2.83
top_words:
  the: 2
  cat: 1
  sat: 1
  on: 1
  mat: 1
```

Text reports print words literally, including non-ASCII words such as `café`,
and round the mean to two decimal places. Top words combine lowercase spellings;
ties retain first-occurrence order. Empty input has zero words, a mean of `0.00`
(`0.0` in JSON), and no top-word entries.

Stdin and multiple files are not supported. Use `--` before a filename that
starts with a hyphen, as in `textstats -- -notes.txt`. The operand `-` is rejected;
use `./-` to read a file with that name.

Exit codes are `0` for a report or help, `1` for a file-read or decoding error,
and `2` for an invalid invocation. Errors go to stderr and leave stdout empty.
Missing files, directories, permission failures, and invalid UTF-8 have specific
diagnostics; other read failures report `textstats: error: cannot read file`.
See [the CLI specification](docs/cli-spec.md) for the complete output contract.

## Test

```bash
pip install -r requirements.txt
pytest
```
