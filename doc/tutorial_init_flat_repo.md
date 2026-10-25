```{eval-rst}
.. meta::
   :description: Step-by-step: create a basic flat `python` repo to be bootstrapped with `protoprimer`
   :keywords: tutorial, flat repo, python, git, pyproject
```

# Init flat repo

Prev: [Tutorial](tutorial_overview.md)

---

The more complex your repo, the more valuable `protoprimer` is.

But we start the demo with the simplest case...

Create a basic `python` project:

```diff
 ^/                                      # repo_root
 │
+├─ pyproject.toml                       # `python` project descriptor for `some_app`
+│
+├─ some_app.py                          # prod code
+├─ test_some_app.py                     # test code
 │
 └─ ...
```

<details>
<summary>[copy & paste & execute]</summary>

<!--- skip: next --->

```shell
# Pick a dir for the new repo:

cd "$( mktemp -d )"
```

<!--- invisible-code-block: python
import tempfile
from pathlib import Path

# The actual dir used below - name/location does not matter:
repo_dir = Path(tempfile.mkdtemp(prefix="protoprimer_manual_"))
--->

```shell
# Disable non-`venv` site-packages for this demo:

export PYTHONNOUSERSITE=1
```

```shell
# Init the repo:

git init
```

<!--- invisible-code-block: shell
git config user.name "protoprimer manual"
git config user.email "manual@protoprimer.invalid"
git config commit.gpgsign false
--->

```shell
# Add the `python` project descriptor - `pyproject.toml`:

cat > pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "some-app"
version = "0.0.0"
dependencies = [
    "pytest",
    "click",
]

[tool.setuptools]
py-modules = ["some_app"]
EOF
```

```shell
# Add prod code - `some_app.py`:

cat > some_app.py <<'EOF'
import click

@click.command()
def some_main():
    click.echo("hello world")

if __name__ == "__main__":
    some_main()
EOF
```

```shell
# Add test code - `test_some_app.py`:

cat > test_some_app.py <<'EOF'
from click.testing import CliRunner

from some_app import some_main

def test_some_main():
    result = CliRunner().invoke(some_main)
    assert result.output == "hello world\n"
    assert result.exit_code == 0
EOF
```

```shell
# Commit everything:

git add --all
git commit --message "Initial commit"
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

</details>

---

Next: [Boot env](tutorial_boot_env.md)
