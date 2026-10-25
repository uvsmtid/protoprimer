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


# The tutorial pages (in the order they are meant to be followed):
# each page continues from the state left by the previous one.
TUTORIAL_PAGES = [
    "tutorial_init_flat_repo.md",
    "tutorial_boot_env.md",
    "tutorial_form_nested_repo.md",
    "tutorial_start_app.md",
    "tutorial_clean_repo_root.md",
    "tutorial_enable_updates.md",
]

# Shared between the pages: `Sybil` creates a separate namespace for each document.
shared_namespace = {}


def load_shared_namespace(namespace):
    namespace.update(shared_namespace)


def save_shared_namespace(namespace):
    shared_namespace.update(namespace)


def pytest_collection_modifyitems(items):
    """
    Run the tutorial pages sequentially (in `TUTORIAL_PAGES` order, not in alphabetical order).
    """
    page_items = [item for item in items if item.path.name in TUTORIAL_PAGES]
    page_items.sort(key=lambda item: TUTORIAL_PAGES.index(item.path.name))
    ordered_items = iter(page_items)
    items[:] = [next(ordered_items) if item.path.name in TUTORIAL_PAGES else item for item in items]


pytest_collect_file = Sybil(
    parsers=[
        PythonCodeBlockParser(),
        CodeBlockParser(language="shell", evaluator=evaluate_shell),
        SkipParser(),
    ],
    patterns=TUTORIAL_PAGES,
    setup=load_shared_namespace,
    teardown=save_shared_namespace,
).pytest()
