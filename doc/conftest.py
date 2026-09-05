import subprocess

from sybil import Sybil
from sybil.parsers.myst import CodeBlockParser, PythonCodeBlockParser


def evaluate_shell(example):
    """
    Runs a `shell` code block in `example.namespace["repo_dir"]`
    (set up by a preceding `python` code block).
    """
    __tracebackhide__ = True
    completed_process = subprocess.run(
        example.parsed,
        shell=True,
        cwd=example.namespace["repo_dir"],
        capture_output=True,
        text=True,
    )
    if completed_process.returncode != 0:
        return "\n".join(
            [
                f"$ {example.parsed}",
                f"exit status: {completed_process.returncode}",
                "stdout:",
                completed_process.stdout,
                "stderr:",
                completed_process.stderr,
            ]
        )


# Executes `python` and `shell` code blocks embedded in the specified docs as `pytest` tests:
pytest_collect_file = Sybil(
    parsers=[
        PythonCodeBlockParser(),
        CodeBlockParser(language="shell", evaluator=evaluate_shell),
    ],
    patterns=[
        "manual.md",
    ],
).pytest()
