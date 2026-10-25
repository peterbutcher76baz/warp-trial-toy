# Textstats command-line interface specification

## Status and approval gate

- Status: **Proposed. Human approval required before implementation.**
- This draft changes documentation only. It does not authorize source, packaging, or test changes.
- The requester must approve this committed specification through the foreman.
- After approval, implementation may continue on this draft PR's branch.
- Draft PR creation, a routing label, or automated checks do not count as approval.
- If the requester changes the contract, update this file and obtain approval again.

## Summary

Add a small command-line interface that computes the library's three statistics for one UTF-8 text file. Provide a terminal report and an optional JSON report. Preserve the existing library behavior. Use only the Python standard library at runtime.

## Product behavior

### 1. Commands and installation

- Installed command: `textstats`.
- Equivalent module invocation: `python -m textstats`.
- Proposed usage: `textstats [-h] [--top N] [--json] FILE`.
- `python -m textstats` accepts the same arguments, output contract, and exit codes.
- After approval, `python -m pip install .` must install the package and the `textstats` command. Editable installation with `python -m pip install -e .` must also work.
- Support Python 3.12 and later. Do not publish a package to a registry as part of this work.

### 2. Arguments and options

- `FILE` is exactly one required file path.
- Resolve a relative path against the process working directory. Accept absolute paths and paths containing spaces.
- Follow symlinks to regular files. Report a dangling symlink as a missing file.
- Reject directories and non-regular files, including FIFOs and devices. Do not wait for input from a special file.
- Do not read stdin. Reject the exact operand `-` with an invocation error. A real file named `-` is available as `./-`.
- Accept `--` to end option parsing: `textstats -- -notes.txt` reads a file named `-notes.txt`.
- `--top N` sets the maximum number of top-word entries. The default is `10`.
- Accept one or more ASCII decimal digits for `N`, including `0` and leading zeros. Reject signs, fractions, exponents, whitespace, and other characters.
- With `--top 0`, keep the word count and mean and return no top-word entries.
- If `N` exceeds the number of distinct normalized lowercase words, return all distinct words.
- Repeated `--top` options use the last value. Repeated `--json` flags have the same effect as one.
- `--json` selects JSON instead of the text report.
- `-h` and `--help` print usage and descriptions of `FILE`, `--top`, `--json`, and help to stdout and exit successfully without opening a file.
- Reject missing operands, extra operands, unknown options, abbreviated long options, and invalid option values. Do not add other options or subcommands.

### 3. Decoding and statistics

- Read the complete file as strict UTF-8, independent of the operating system locale.
- Fail on invalid UTF-8. Do not guess another encoding or replace or discard invalid bytes.
- Do not provide an `--encoding` option in this version.
- Preserve a UTF-8 BOM as the character U+FEFF. It participates in statistics exactly as it does when passed to the current library functions.
- Compute every statistic through the public functions exported by `textstats/__init__.py:1`.
- Preserve the behavior of `textstats/core.py:10`, `textstats/core.py:22`, `textstats/core.py:26`, and `textstats/core.py:33`:
  - Split words on whitespace.
  - Strip ASCII `string.punctuation` and Unicode category `P` characters from each word's edges.
  - Discard tokens that become empty.
  - Preserve internal punctuation, including apostrophes and hyphens.
  - Compute the mean from Python character lengths, not byte lengths or display widths.
  - Combine top-word counts using `str.lower()`, not Unicode case folding.
  - Sort top words by decreasing count. Preserve first-occurrence order for ties.
- Empty files, whitespace-only files, and punctuation-only files have zero words, a mean of `0.0`, and no top words.
- Read the file and compute the report before writing report bytes. An input error must not leave a partial report on stdout.

### 4. Text output

Print these lines in this order:

```text path=null start=null
word_count: 6
mean_word_length: 2.83
top_words:
  "the": 2
  "cat": 1
  "sat": 1
  "on": 1
  "mat": 1
```

- This example is the exact default output for a file containing `The cat sat on the mat`.
- Print the count as a decimal integer.
- Format the mean with Python's `format(value, ".2f")`. Always print two fractional digits and a decimal point, independent of locale.
- Each top-word entry has two leading spaces, a quoted word, `: `, and its integer count.
- Render a word with the equivalent of `json.dumps(word, ensure_ascii=True)`. Escape quotes, backslashes, control characters, and non-ASCII characters. This makes word boundaries unambiguous and output safe for non-UTF-8 terminals.
- For example, the word `café` renders as `"caf\u00e9"`. JSON decoding that string restores the original Unicode word.
- If there are no entries, print only the three field lines. Do not print `(none)`, `[]`, an extra blank line, or placeholder entries.
- End every line, including the final line, with `\n`. Do not print a filename, progress messages, color, or a banner.

### 5. JSON output

For the same six-word example, `--json` prints exactly:

```json path=null start=null
{"word_count": 6, "mean_word_length": 2.8333333333333335, "top_words": [{"word": "the", "count": 2}, {"word": "cat", "count": 1}, {"word": "sat", "count": 1}, {"word": "on", "count": 1}, {"word": "mat", "count": 1}]}
```

- Print one JSON object on one line, followed by `\n`.
- Emit exactly these keys in the displayed order: `word_count`, `mean_word_length`, `top_words`.
- `word_count` is an integer. `mean_word_length` is the library's unrounded floating-point value. `top_words` is an array.
- Each array entry has exactly `word` and `count`, in that order. `word` is a string and `count` is a positive integer.
- Preserve top-word order in the array.
- Use standard `json.dumps` spacing: one space after a colon or comma. Use `ensure_ascii=True` and no indentation.
- Empty input prints exactly `{"word_count": 0, "mean_word_length": 0.0, "top_words": []}` followed by `\n`.
- Do not include the path, encoding, top limit, or a schema-version field.

### 6. Diagnostics and exit codes

- Exit `0` for a complete report or help. Stderr is empty.
- Exit `1` for an anticipated filesystem, input-decoding, or output-writing failure.
- Exit `2` for an invalid invocation.
- Diagnostics go only to stderr. Do not emit JSON error objects, even with `--json`.
- Every application diagnostic ends with `\n` and starts with `textstats: error: `.
- In the following templates, `PATH` means the supplied operand encoded with `json.dumps(path, ensure_ascii=True)`. Preserve the supplied spelling; do not expand it to an absolute path in messages.
- Use these exact application diagnostic lines:
  - Missing file or dangling symlink: `textstats: error: file not found: PATH`.
  - Directory: `textstats: error: expected a file, got a directory: PATH`.
  - Other non-regular file: `textstats: error: expected a regular file: PATH`.
  - Permission failure while inspecting or reading: `textstats: error: permission denied: PATH`.
  - Invalid UTF-8: `textstats: error: invalid UTF-8: PATH`.
  - Other operating-system error while inspecting or reading: `textstats: error: cannot read file: PATH`.
  - Output write or encoding failure, including a broken pipe: `textstats: error: cannot write output`.
- Invocation errors use `argparse` usage and a `textstats: error: ...` line on stderr. Exact argparse wrapping and wording are not part of the contract. The error must identify the missing or invalid argument or option.
- Reject operand `-` as an invocation error that says stdin is unsupported.
- Parse and validate arguments before any filesystem access.
- Do not use a preflight permission-bit check instead of attempting the read. Report read-time failures, including a file removed after inspection.
- Anticipated failures must not print a traceback. Do not hide programming errors behind a broad catch-all exception handler.
- Stdout is empty for invocation and input errors. A write failure can occur after some output has reached its destination; atomic delivery cannot be guaranteed.

## Examples

- `textstats essay.txt`: text report with at most ten top words.
- `textstats --top 3 "draft essay.txt"`: text report with at most three entries.
- `python -m textstats --json --top 0 essay.txt`: JSON count and full-precision mean with an empty top-word array.
- `textstats -- -notes.txt`: read a filename that starts with a hyphen.
- `textstats missing.txt`: empty stdout, exit `1`, and stderr `textstats: error: file not found: "missing.txt"` followed by `\n`.
- `textstats --top -1 essay.txt`: empty stdout, exit `2`, and an argument error on stderr.
- A file with UTF-8 bytes `EF BB BF 63 61 74` contains the single word U+FEFF followed by `cat`. Its count is `1`, its mean is `4.0`, and its text entry is `  "\ufeffcat": 1`.

## Technical design after approval

- Add `textstats/cli.py` with `main(argv: list[str] | None = None) -> int`.
- Build an `argparse.ArgumentParser` with `prog="textstats"` and `allow_abbrev=False`. Keep parsing, file errors, and formatting at the CLI boundary.
- Use a text codec with UTF-8 strict behavior. Do not use `utf-8-sig`.
- Call the three public functions. Build one result object before choosing the output renderer.
- Add a thin `textstats/__main__.py` that exits with the result of `main()`. Importing the library must not execute the CLI.
- Extend `pyproject.toml:1` with a setuptools build backend, explicit discovery of only `textstats`, project name `textstats`, initial project version `0.1.0`, Python requirement `>=3.12`, and console script `textstats = "textstats.cli:main"`. Preserve the pytest configuration.
- Build requirements may use `setuptools>=68`. Runtime dependencies remain empty. Do not change the public exports or algorithms.
- After approval, update `README.md` with local installation, both invocation forms, options, output, exit codes, and UTF-8-only input.
- Add CLI coverage in `tests/test_cli.py`. Keep the existing 16 tests in `tests/test_core.py` unchanged.

## Decisions and alternatives

- **One file, no stdin:** this matches the requested file workflow and provides clear path errors. Stdin and multiple files would need stream or aggregate-result contracts and are deferred.
- **Installed command plus module invocation:** the installed name is short; the module invocation works without a shell entry-point lookup. Module-only delivery avoids metadata but does not provide the requested installed command.
- **All statistics with a top limit:** a fixed report is predictable. Individual stat flags add combinations without a stated need. Default ten entries gives a bounded report; zero provides counts and mean without a word list.
- **Strict UTF-8 only:** this is deterministic across machines. Autodetection can produce silently incorrect text. A codec override supports legacy files but adds configuration and unknown-codec errors; it is deferred.
- **Retain the BOM:** this matches direct library calls on strict UTF-8-decoded text. Stripping it is more convenient for some editors but introduces a separate CLI normalization rule.
- **Text plus opt-in JSON:** text supports inspection; JSON supports scripts without parsing presentation. JSON-only is less convenient interactively; text-only is brittle for automation.
- **ASCII-safe quoted words:** this preserves Unicode and prevents terminal-control interpretation. Literal Unicode is more readable but depends on stdout encoding. Text means are rounded for readability; JSON means retain the library value for scripts.
- **Separate usage and runtime exits:** `2` distinguishes an invalid command from an inaccessible or undecodable file (`1`). Per-error exit codes would expand the public interface without a stated need.
- **Minimal setuptools packaging:** it supplies the entry point without a runtime dependency. Distribution publishing and a broader build pipeline are not required.

## Assumptions

- Every concrete default above is a **proposed assumption for human approval**, not an already-approved product decision.
- The requester has not selected the command spelling, top count, formats, precision, supported Python versions, packaging version, or error-code convention.
- The foreman explicitly authorized drafting these bounded defaults instead of a blocking interview. The written spec approval is the decision gate.
- The entire file fits in memory. There is no streaming or large-file performance guarantee in this version.
- Files do not change during a successful read. Read-time operating-system failures are handled, but this work does not provide snapshot semantics.

## Out of scope

- Implementation before explicit human approval of this spec.
- Stdin, multiple input files, recursive directory processing, and special-file input.
- Encoding detection, codec overrides, lossy decoding, and BOM removal.
- New statistics, tokenization changes, different case normalization, or different tie-breaking.
- Per-stat selection, output files, CSV, color, interactive behavior, and registry publishing.
- An unrelated formatter, linter, type-checker, dependency cleanup, or CI redesign.

## Validation criteria

All tests and commands below are future implementation requirements. Do not create or run the proposed CLI during this documentation-only stage.

- `test_cli_default_text`: subprocess output for `The cat sat on the mat` matches the text example byte-for-byte, including final newline. Exit is `0`; stderr is empty.
- `test_cli_json`: parse the JSON example and compare exact bytes, key order, numeric types, top-word order, and unrounded mean.
- `test_cli_top_limits`: cover omitted `--top` with more than ten distinct words, `--top 2`, `--top 0`, `--top 100`, leading zeros, and last-value-wins repetition.
- `test_cli_library_parity`: compare CLI JSON against all three public API calls for mixed case, tied counts, internal punctuation, ASCII edge punctuation, Unicode punctuation, and non-ASCII words.
- `test_cli_empty_inputs`: cover zero-byte, whitespace-only, and punctuation-only files. Assert exact text and JSON empty outputs.
- `test_cli_bom_preserved`: use the BOM bytes in the example and assert the exact word, count, mean, and escaped text.
- `test_cli_escaped_words`: cover quotes, backslashes, an embedded control character, and Unicode. Assert ASCII-only reports and lossless JSON decoding of words. Exercise stdout with an ASCII encoding.
- `test_cli_paths`: cover relative and absolute paths, spaces, `-- -notes.txt`, `./-`, a regular-file symlink, and a dangling symlink.
- `test_cli_file_errors`: cover missing file, directory, and FIFO; assert exact diagnostics, exit `1`, empty stdout, no traceback, and no blocking on the FIFO.
- `test_cli_read_failures`: simulate `PermissionError` and other `OSError` values during inspection and reading. Also simulate disappearance after inspection. Assert exact diagnostics and no partial report. Do not rely only on Unix permission bits; privileged CI may still read such files.
- `test_cli_invalid_utf8`: use bytes `FF`, and valid text followed by `FF`; assert exact decode diagnostic, exit `1`, and empty stdout in both formats.
- `test_cli_usage_errors`: cover no operand, two operands, `-`, unknown or abbreviated options, missing `--top` value, negative and malformed values, and unsupported `--encoding`. Assert exit `2`, empty stdout, useful stderr, and no file access.
- `test_cli_help`: exercise both help spellings for both invocation forms without a file; assert exit `0`, empty stderr, and descriptions of every accepted argument and option.
- `test_cli_output_failure`: simulate a write-time `OSError`, `UnicodeEncodeError`, and `BrokenPipeError`; assert exit `1` and the output diagnostic without a traceback.
- `test_cli_import_safe`: import `textstats` and `textstats.cli` without parsing arguments, reading input, or emitting output.
- Install in a fresh virtual environment with `python -m pip install -r requirements.txt` and `python -m pip install .`. From a temporary working directory outside this checkout, run the same fixture through `textstats` and `python -m textstats`. Compare stdout, stderr, and status for text, JSON, errors, and help. Repeat entry-point smoke checks after `python -m pip install -e .`.
- Run `python -m pytest -q` and `python -m compileall -q textstats` on Python 3.12. All existing and new tests must pass. No linter or type checker is configured in this repository.
- The CLI has no graphical interface. Byte-exact subprocess output is the required proof; browser screenshots or recordings are not applicable.
- Before handing implementation to review, record the requester's explicit spec approval and its reference. A green test run does not replace that approval.
