import argparse
import json
from pathlib import Path
import sys

from textstats import mean_word_length, top_words, word_count


def _top_limit(value: str) -> int:
    if not value.isascii() or not value.isdecimal():
        raise argparse.ArgumentTypeError("expected a nonnegative decimal integer")
    return int(value)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="textstats",
        description="Report word statistics for a UTF-8 text file.",
        allow_abbrev=False,
    )
    parser.add_argument(
        "file", metavar="FILE", help="UTF-8 file with an optional initial BOM"
    )
    parser.add_argument(
        "--top",
        metavar="N",
        type=_top_limit,
        default=10,
        help="maximum number of top words (default: 10; 0 omits entries)",
    )
    parser.add_argument("--json", action="store_true", help="print a JSON report")
    args = parser.parse_args(argv)
    if args.file == "-":
        parser.error("stdin is unsupported; provide a file path")

    try:
        text = Path(args.file).read_text(encoding="utf-8-sig", errors="strict")
    except (OSError, UnicodeDecodeError) as error:
        path = json.dumps(args.file, ensure_ascii=True)
        if isinstance(error, FileNotFoundError):
            message = f"file not found: {path}"
        elif isinstance(error, IsADirectoryError):
            message = f"expected a file, got a directory: {path}"
        elif isinstance(error, PermissionError):
            message = f"permission denied: {path}"
        elif isinstance(error, UnicodeDecodeError):
            message = f"invalid UTF-8: {path}"
        else:
            message = "cannot read file"
        print(f"textstats: error: {message}", file=sys.stderr)
        return 1

    result = {
        "word_count": word_count(text),
        "mean_word_length": mean_word_length(text),
        "top_words": [
            {"word": word, "count": count}
            for word, count in top_words(text, args.top)
        ],
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=True))
    else:
        print(f"word_count: {result['word_count']}")
        print(f"mean_word_length: {result['mean_word_length']:.2f}")
        print("top_words:")
        for entry in result["top_words"]:
            print(f"  {entry['word']}: {entry['count']}")
    return 0
