# Manual

The more complex setup your repo has, the more valuable `protoprimer` is.

But we need to demo the simplest case first.

## Simple repo

[`min leaps shape`][FT_59_95_81_63.tree_shape.md] is the simplest repo dir tree shape.

<!--- invisible-code-block: python
import tempfile
from pathlib import Path

repo_dir = Path(tempfile.mkdtemp(prefix="protoprimer_manual_"))
--->

Init the repo:

```shell
git init --quiet
git config user.name "protoprimer manual"
git config user.email "manual@protoprimer.invalid"
git config commit.gpgsign false
```

Add the `python` project spec for `some_app`:

```shell
cat > pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "some-app"
version = "0.1.0"
description = "min leaps shape example"

[tool.setuptools.packages.find]
where = ["src"]
EOF
```

Add prod code:

```shell
cat > some_app.py <<'EOF'
def main():
    print("hello world")


if __name__ == "__main__":
    main()
EOF
```

Add test code:

```shell
cat > test_some_app.py <<'EOF'
from some_app import main


def test_main(capsys):
    main()
    captured = capsys.readouterr()
    assert captured.out == "hello world\n"
EOF
```

Commit everything:

```shell
git add --all
git commit --quiet --message "Initial commit"
```

<!--- invisible-code-block: python
import subprocess

commit_count = subprocess.run(
    ["git", "rev-list", "--count", "HEAD"],
    cwd=repo_dir,
    capture_output=True,
    text=True,
    check=True,
).stdout.strip()
assert commit_count == "1", commit_count

repo_status = subprocess.run(
    ["git", "status", "--porcelain"],
    cwd=repo_dir,
    capture_output=True,
    text=True,
    check=True,
).stdout
assert repo_status == "", repo_status
--->

<!--- invisible-code-block: python
import shutil

shutil.rmtree(repo_dir, ignore_errors=True)
--->

[FT_59_95_81_63.tree_shape.md]: feature_topic/FT_59_95_81_63.tree_shape.md
