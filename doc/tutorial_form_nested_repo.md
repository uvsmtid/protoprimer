```{eval-rst}
.. meta::
   :description: Step-by-step: convert a flat repo into a nested one and reconfigure `proto_kernel.py`
   :keywords: tutorial, nested repo, project dir, proto_kernel, config
```

# Form nested repo

Prev: [Boot env](tutorial_boot_env.md)

---

We can move project files into the `src` directory.

This requires configuring `proto_kernel.py` (via `proto_kernel.json`) to find the project files:

```diff
 ^/
 │
 ├─ proto_kernel.py
+├─ proto_kernel.json                    # <- configure
 ├─ .python-version
 │
-├─ pyproject.toml                       # move ->
-│
-├─ some_app.py                          # move ->
-├─ test_some_app.py                     # move ->
 │
+├─ src/
+│  │
+│  ├─ some_app/                         # project dir
+│  │  │
+│  │  ├─ pyproject.toml                 # <- move
+│  │  │
+│  │  ├─ main/                          # prod code
+│  │  │  │
+│  │  │  └─ some_app.py                 # <- move
+│  │  │
+│  │  └─ test/                          # test code
+│  │     │
+│  │     └─ test_some_app.py            # <- move
+│  └─ ...
 └─ ...
```

<details>
<summary>[copy & paste & execute]</summary>

```shell
# Move code under `src/some_app/`:

mkdir -p src/some_app/main
mkdir -p src/some_app/test

git mv pyproject.toml src/some_app/pyproject.toml
git mv some_app.py src/some_app/main/some_app.py
git mv test_some_app.py src/some_app/test/test_some_app.py
```

```shell
# Adjust `pyproject.toml`:

cat > src/some_app/pyproject.toml <<'EOF'
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

[tool.setuptools.package-dir]
"" = "main"
EOF
```

```shell
# Configure `proto_kernel.py` for the updated project structure:

cat > proto_kernel.json <<'EOF'
{
    "global_conf_dir_rel_path": ".",
    "project_descriptors": [
        {
            "build_root_dir_rel_path": "src/some_app"
        }
    ]
}
EOF
```

```shell
# Drop `some_app.egg-info` - it no longer builds at the repo root:

cat > .gitignore <<'EOF'
/constraints.txt
/log/
/venv/
/cache/
EOF
```

```shell
# Ignore `some_app.egg-info` under project dir - it now builds there:

cat > src/some_app/.gitignore <<'EOF'
/main/some_app.egg-info/
EOF
```

```shell
# Commit everything:

git add --all
git commit --message "Move project files under ./src/some_app/"
```

</details>

<!--- invisible-code-block: python
proto_kernel_json_path = repo_dir / "proto_kernel.json"
assert proto_kernel_json_path.exists(), proto_kernel_json_path

commit_count = subprocess.run(
    ["git", "rev-list", "--count", "HEAD"],
    cwd=repo_dir,
    capture_output=True,
    text=True,
    check=True,
).stdout.strip()
assert commit_count == "3", commit_count

repo_status = subprocess.run(
    ["git", "status", "--porcelain"],
    cwd=repo_dir,
    capture_output=True,
    text=True,
    check=True,
).stdout
assert repo_status == "", repo_status
--->

Re-run the bootstrap to confirm it still works:

```shell
./proto_kernel.py
```

<!--- invisible-code-block: python
repo_status = subprocess.run(
    ["git", "status", "--porcelain"],
    cwd=repo_dir,
    capture_output=True,
    text=True,
    check=True,
).stdout
assert repo_status == "", repo_status
--->

---

Next: [Start app](tutorial_start_app.md)
