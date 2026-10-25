```{eval-rst}
.. meta::
   :description: Step-by-step: start an app from `venv` via `protoprimer` with `start_app`
   :keywords: tutorial, start_app, entry_script, venv, python, repo
```

# Start app

Prev: [Form nested repo](tutorial_form_nested_repo.md)

---

## Problem

The next most obvious problem is the inconvenience of:

```shell
./venv/bin/python src/some_app/main/some_app.py
```

*   specifying the correct `path/to/python` interpreter
*   specifying the correct `path/to/some_app.py` within sources

## Solution

Implement an [entry_script][FT_75_87_82_46.entry_script.md] that switches to `venv` to invoke the app:

```diff
 ^/
 │
 ├─ proto_kernel.py
 ├─ proto_kernel.json
 ├─ .python-version
 │
+├─ cmd/
+│  │
+│  └─ some_app                          # <- entry_script
 │
 ├─ src/
 │  │
 │  ├─ some_app/
 │  │  │
 │  │  ├─ pyproject.toml
 │  │  │
 │  │  ├─ main/
 │  │  │  │
 │  │  │  └─ some_app.py
 │  │  │
 │  │  └─ test/
 │  │     │
 │  │     └─ test_some_app.py
 │  └─ ...
 └─ ...
```

<details>
<summary>[copy & paste & execute]</summary>

```shell
# Generate entry script `./cmd/some_app` invoking `some_app:some_main` from `venv`:

mkdir -p cmd

./proto_kernel.py wrap start_app \
    --entry_script_path "./cmd/some_app" \
    --main_func "some_app:some_main"
```

```shell
# Commit everything:

git add --all
git commit --message "Add ./cmd/some_app entry script"
```

<!--- invisible-code-block: python
entry_script_path = repo_dir / "cmd" / "some_app"
assert entry_script_path.exists(), entry_script_path
assert entry_script_path.stat().st_mode & 0o111, "not executable"

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

Now you can start the app via the dedicated `entry_script`:

```shell
./cmd/some_app
```

```output
hello world
```

It works via [start_app][FT_05_08_64_67.start_app.md] function of [proto_kernel][FT_87_17_49_36.proto_kernel.md]:

*   **no** explicit activation of individual `venv`-s **per repo clone**
*   **no** worrying about incompatibility between branches **per repo clone**
*   **no** `#!shebang` absolute path exposure and length limit **per repo clone**

<!--- invisible-code-block: python
entry_script_process = subprocess.run(
    ["cmd/some_app"],
    cwd=repo_dir,
    capture_output=True,
    text=True,
)
assert entry_script_process.returncode == 0, entry_script_process.stdout + entry_script_process.stderr
assert entry_script_process.stdout == "hello world\n", entry_script_process.stdout
--->

<!--- invisible-code-block: python
# Any function can be called without a dedicated `entry_script`:
start_process = subprocess.run(
    [
        "./proto_kernel.py",
        "start",
        "some_app:some_main",
    ],
    cwd=repo_dir,
    capture_output=True,
    text=True,
)
assert start_process.returncode == 0, start_process.stdout + start_process.stderr
assert start_process.stdout == "hello world\n", start_process.stdout
--->

[FT_05_08_64_67.start_app.md]: feature_topic/FT_05_08_64_67.start_app.md
[FT_75_87_82_46.entry_script.md]: feature_topic/FT_75_87_82_46.entry_script.md
[FT_87_17_49_36.proto_kernel.md]: feature_topic/FT_87_17_49_36.proto_kernel.md

---

Next: [Clean repo root](tutorial_clean_repo_root.md)
