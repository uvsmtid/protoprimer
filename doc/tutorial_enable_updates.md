```{eval-rst}
.. meta::
   :description: Step-by-step: keep `proto_kernel.py` up-to-date by adding `protoprimer` as a dependency
   :keywords: tutorial, auto-update, proto_kernel, protoprimer, dependency
```

# Enable updates

Prev: [Clean repo root](tutorial_clean_repo_root.md)

---

`proto_kernel.py` is both:
*   a standalone script
*   a copy of the `protoprimer.primer_kernel` module

To keep it up-to-date, add `protoprimer` as a dependency in `pyproject.toml`.

```diff
 dependencies = [
     "click",
+    # Keeps hosted copy `proto_kernel.py` updated:
+    "protoprimer",
 ]
```

<details>
<summary>[copy & paste & execute]</summary>

```shell
# Add `protoprimer` as a dependency in `pyproject.toml`:

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
    # TODO: Point to specific released version compatible with this doc:
    "protoprimer @ git+https://github.com/uvsmtid/protoprimer.git#subdirectory=src/protoprimer",
]

[tool.setuptools]
py-modules = ["some_app"]

[tool.setuptools.package-dir]
"" = "main"
EOF
```

```shell
# Commit everything:

git add --all
git commit --message "Add protoprimer as a dependency"
```

<!--- invisible-code-block: python
# Pin to the commit checked out here (a commit sha works for any `pip` version, unlike a branch name or `HEAD`):
# `localhost` netloc: older `packaging` (via `setuptools` resolved for Python 3.7) rejects an empty one.
local_repo_uri = local_repo_dir.as_uri().replace("file:///", "file://localhost/")
some_app_pyproject_toml_path = repo_dir / "src" / "some_app" / "pyproject.toml"
some_app_pyproject_toml_text = some_app_pyproject_toml_path.read_text()
some_app_pyproject_toml_text = some_app_pyproject_toml_text.replace(
    "protoprimer @ git+https://github.com/uvsmtid/protoprimer.git#subdirectory=src/protoprimer",
    f"protoprimer @ git+{local_repo_uri}@{local_commit_sha}#subdirectory=src/protoprimer",
)
some_app_pyproject_toml_path.write_text(some_app_pyproject_toml_text)

subprocess.run(
    ["git", "commit", "--all", "--message", "Pin `protoprimer` dependency to the current commit for this test"],
    cwd=repo_dir,
    check=True,
)

pyproject_toml_text = some_app_pyproject_toml_path.read_text()
assert "protoprimer @ git+" in pyproject_toml_text, pyproject_toml_text

commit_count = subprocess.run(
    ["git", "rev-list", "--count", "HEAD"],
    cwd=repo_dir,
    capture_output=True,
    text=True,
    check=True,
).stdout.strip()
assert commit_count == "8", commit_count

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

<!--- invisible-code-block: python
proto_kernel_copy_path = repo_dir / "src" / "proto_code" / "proto_kernel.py"
--->

Re-run the bootstrap to update:

```shell
./prime
```

<!--- invisible-code-block: python
proto_kernel_text_after_update = proto_kernel_copy_path.read_text()
assert "protoprimer.primer_kernel" in proto_kernel_text_after_update

# Any resulting change is confined to `proto_kernel.py` (nothing else is touched):
repo_status = subprocess.run(
    ["git", "status", "--porcelain"],
    cwd=repo_dir,
    capture_output=True,
    text=True,
    check=True,
).stdout
for status_line in repo_status.splitlines():
    assert status_line.endswith("src/proto_code/proto_kernel.py"), repo_status

# The app still starts:
entry_script_process = subprocess.run(
    ["cmd/some_app"],
    cwd=repo_dir,
    capture_output=True,
    text=True,
)
assert entry_script_process.returncode == 0, entry_script_process.stdout + entry_script_process.stderr
assert entry_script_process.stdout == "hello world\n", entry_script_process.stdout
--->

`proto_kernel.py` will match the version of `protoprimer.primer_kernel` pinned in the `venv`.

<!--- invisible-code-block: python
import shutil

shutil.rmtree(repo_dir, ignore_errors=True)
--->

---

Back: [Tutorial](tutorial_overview.md)
