import subprocess

from sybil import Sybil
from sybil.parsers.myst import CodeBlockParser, PythonCodeBlockParser, SkipParser


def evaluate_shell(code_example):
    """
    Executes `shell` code blocks embedded in the specified docs as `pytest` tests.
    """
    __tracebackhide__ = True
    completed_process = subprocess.run(
        code_example.parsed,
        shell=True,
        cwd=code_example.namespace["repo_dir"],
        capture_output=True,
        text=True,
    )
    if completed_process.returncode != 0:
        return "\n".join(
            [
                f"code example: {code_example.parsed}",
                f"exit code: {completed_process.returncode}",
                "stdout:",
                completed_process.stdout,
                "stderr:",
                completed_process.stderr,
            ]
        )


pytest_collect_file = Sybil(
    parsers=[
        PythonCodeBlockParser(),
        CodeBlockParser(language="shell", evaluator=evaluate_shell),
        SkipParser(),
    ],
    patterns=[
        "runtime.md",
    ],
).pytest()
