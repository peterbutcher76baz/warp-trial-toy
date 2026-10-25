import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from textstats import mean_word_length, top_words, word_count


@pytest.fixture
def run_cli(tmp_path):
    def run(*args):
        return subprocess.run(
            [sys.executable, "-m", "textstats", *map(str, args)],
            cwd=tmp_path,
            env={
                **os.environ,
                "PYTHONPATH": str(Path(__file__).resolve().parents[1]),
                "PYTHONIOENCODING": "utf-8",
            },
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    return run


@pytest.fixture
def sample_file(tmp_path):
    path = tmp_path / "sample.txt"
    path.write_text("The cat sat on the mat", encoding="utf-8")
    return path


def test_cli_default_text(run_cli, sample_file):
    result = run_cli(sample_file)
    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout == (
        "word_count: 6\n"
        "mean_word_length: 2.83\n"
        "top_words:\n"
        "  the: 2\n"
        "  cat: 1\n"
        "  sat: 1\n"
        "  on: 1\n"
        "  mat: 1\n"
    )


def test_cli_json(run_cli, sample_file):
    result = run_cli("--json", sample_file)
    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout == (
        '{"word_count": 6, "mean_word_length": 2.8333333333333335, '
        '"top_words": [{"word": "the", "count": 2}, {"word": "cat", "count": 1}, '
        '{"word": "sat", "count": 1}, {"word": "on", "count": 1}, '
        '{"word": "mat", "count": 1}]}\n'
    )


@pytest.mark.parametrize(
    ("options", "limit"),
    [
        ([], 10),
        (["--top", "2"], 2),
        (["--top", "0"], 0),
        (["--top", "100"], 12),
        (["--top", "002"], 2),
        (["--top", "0", "--top", "2", "--json"], 2),
    ],
)
def test_cli_top_limits(run_cli, sample_file, options, limit):
    words = "zero one two three four five six seven eight nine ten eleven".split()
    sample_file.write_text(" ".join(words), encoding="utf-8")
    result = run_cli("--json", *options, sample_file)
    assert result.returncode == 0
    assert result.stderr == ""
    assert json.loads(result.stdout) == {
        "word_count": 12,
        "mean_word_length": sum(map(len, words)) / 12,
        "top_words": [{"word": word, "count": 1} for word in words[:limit]],
    }


def test_cli_library_parity(run_cli, sample_file):
    text = "“CaT” $cat+ don't re-enter café CAFÉ Straße STRASSE … — \ufeffcat"
    sample_file.write_text(text, encoding="utf-8")
    result = run_cli("--json", sample_file)
    assert result.returncode == 0
    assert result.stderr == ""
    assert json.loads(result.stdout) == {
        "word_count": word_count(text),
        "mean_word_length": mean_word_length(text),
        "top_words": [
            {"word": word, "count": count} for word, count in top_words(text, 10)
        ],
    }


@pytest.mark.parametrize("content", [b"", b" \t\n ", "!!! … —".encode(), b"\xef\xbb\xbf"])
def test_cli_empty_inputs(run_cli, sample_file, content):
    sample_file.write_bytes(content)
    text = run_cli(sample_file)
    assert text.returncode == 0
    assert text.stderr == ""
    assert text.stdout == "word_count: 0\nmean_word_length: 0.00\ntop_words:\n"
    report = run_cli("--json", sample_file)
    assert report.returncode == 0
    assert report.stderr == ""
    assert report.stdout == (
        '{"word_count": 0, "mean_word_length": 0.0, "top_words": []}\n'
    )


@pytest.mark.parametrize("options", [[], ["--json"]])
def test_cli_bom_stripped(run_cli, sample_file, options):
    sample_file.write_bytes(b"cat cat")
    plain = run_cli(*options, sample_file)
    sample_file.write_bytes(b"\xef\xbb\xbfcat cat")
    bom = run_cli(*options, sample_file)
    assert (bom.returncode, bom.stdout, bom.stderr) == (
        plain.returncode,
        plain.stdout,
        plain.stderr,
    )
    assert bom.returncode == 0
    assert bom.stderr == ""
    if options:
        assert json.loads(bom.stdout) == {
            "word_count": 2,
            "mean_word_length": 3.0,
            "top_words": [{"word": "cat", "count": 2}],
        }
    else:
        assert bom.stdout == (
            "word_count: 2\nmean_word_length: 3.00\ntop_words:\n  cat: 2\n"
        )


def test_cli_unicode_output(run_cli, sample_file):
    sample_file.write_text("café café", encoding="utf-8")
    text = run_cli(sample_file)
    assert text.returncode == 0
    assert text.stderr == ""
    assert text.stdout == (
        "word_count: 2\nmean_word_length: 4.00\ntop_words:\n  café: 2\n"
    )
    report = run_cli("--json", sample_file)
    assert report.returncode == 0
    assert report.stderr == ""
    assert report.stdout == (
        '{"word_count": 2, "mean_word_length": 4.0, '
        '"top_words": [{"word": "caf\\u00e9", "count": 2}]}\n'
    )
    assert json.loads(report.stdout)["top_words"] == [{"word": "café", "count": 2}]


@pytest.mark.parametrize(
    "operand", ["notes.txt", "draft notes.txt", "-notes.txt", "./-", "absolute"]
)
def test_cli_paths(run_cli, tmp_path, operand):
    path = tmp_path / operand
    path.write_text("cat", encoding="utf-8")
    args = [str(path)] if operand == "absolute" else ["--", operand]
    result = run_cli(*args)
    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout == (
        "word_count: 1\nmean_word_length: 3.00\ntop_words:\n  cat: 1\n"
    )


@pytest.mark.parametrize(
    ("operand", "message"),
    [
        ('missing café".txt', "file not found"),
        (".", "expected a file, got a directory"),
    ],
)
def test_cli_file_errors(run_cli, operand, message):
    result = run_cli("--json", operand)
    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr == f"textstats: error: {message}: {json.dumps(operand)}\n"


@pytest.mark.parametrize(
    ("error", "message"),
    [
        (PermissionError("private details"), 'permission denied: "sample.txt"'),
        (OSError("private details"), "cannot read file"),
    ],
)
def test_cli_read_failures(monkeypatch, capsys, error, message):
    from textstats.cli import main

    def fail_read(self, **kwargs):
        raise error

    monkeypatch.setattr(Path, "read_text", fail_read)
    assert main(["--json", "sample.txt"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == f"textstats: error: {message}\n"


@pytest.mark.parametrize("content", [b"\xff", b"valid text \xff"])
@pytest.mark.parametrize("options", [[], ["--json"]])
def test_cli_invalid_utf8(run_cli, sample_file, content, options):
    sample_file.write_bytes(content)
    result = run_cli(*options, sample_file)
    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr == (
        f"textstats: error: invalid UTF-8: {json.dumps(str(sample_file))}\n"
    )


@pytest.mark.parametrize(
    ("args", "message"),
    [
        ([], "FILE"),
        (["one.txt", "two.txt"], "two.txt"),
        (["-"], "stdin"),
        (["--unknown", "sample.txt"], "--unknown"),
        (["--js", "sample.txt"], "--js"),
        (["--to", "2", "sample.txt"], "--to"),
        (["sample.txt", "--top"], "--top"),
        (["--encoding", "utf-8", "sample.txt"], "--encoding"),
        *[
            (["sample.txt", "--top", value], "--top")
            for value in ["-1", "+1", "1.5", "1e2", " 1", "1 ", "one", "١", ""]
        ],
    ],
)
def test_cli_usage_errors(monkeypatch, capsys, args, message):
    from textstats.cli import main

    def unexpected_read(self, **kwargs):
        pytest.fail("invalid arguments must not read a file")

    monkeypatch.setattr(Path, "read_text", unexpected_read)
    with pytest.raises(SystemExit) as error:
        main(args)
    assert error.value.code == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "usage: textstats" in captured.err
    assert "textstats: error:" in captured.err
    assert message in captured.err
    assert "Traceback" not in captured.err


@pytest.mark.parametrize("option", ["-h", "--help"])
def test_cli_help(run_cli, option):
    result = run_cli(option)
    assert result.returncode == 0
    assert result.stderr == ""
    for description in ["usage: textstats", "FILE", "--top N", "--json", "--help"]:
        assert description in result.stdout


def test_cli_import_safe(capsys, monkeypatch):
    import importlib
    import textstats

    def unexpected_read(self, **kwargs):
        pytest.fail("importing must not read a file")

    monkeypatch.setattr(Path, "read_text", unexpected_read)
    monkeypatch.setattr(sys, "argv", ["textstats", "--invalid-option"])
    importlib.reload(textstats)
    importlib.reload(importlib.import_module("textstats.cli"))
    captured = capsys.readouterr()
    assert captured.out == captured.err == ""
