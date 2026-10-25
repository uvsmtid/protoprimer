```{eval-rst}
.. meta::
   :description: Step-by-step: move `proto_code` away from the repo root and add `./prime`
   :keywords: tutorial, proto_code, entry_script, prime, repo root
```

# Clean repo root

Prev: [Start app](tutorial_start_app.md)

---

## Dedicated source dir

[proto_code][FT_90_65_67_62.proto_code.md] is anything running outside `venv`.

We can move `proto_code` under a dedicated dir to avoid clutter in the repo root.

```diff
 ^/
 │
-├─ proto_kernel.py                      # move ->
-├─ proto_kernel.json                    # move ->
-├─ .python-version                      # move ->
 │
 ├─ cmd/
 │  │
 │  └─ some_app
 │
 ├─ src/
 │  │
+│  ├─ proto_code/                       # <- dedicated source dir for proto_code
+│  │  │
+│  │  ├─ proto_kernel.py                # <- move
+│  │  ├─ proto_kernel.json              # <- move
+│  │  ├─ .python-version                # <- move
 │  │  │
 │  │  └─ ...
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
# Move `proto_code` files under `src/proto_code/`:

mkdir -p src/proto_code

git mv proto_kernel.py   src/proto_code/proto_kernel.py
git mv proto_kernel.json src/proto_code/proto_kernel.json
git mv .python-version   src/proto_code/.python-version
```

```shell
# Remove bootstrap artifacts from the old `ref_root` (repo root):

rm -rf venv log cache constraints.txt __pycache__
```

```shell
# Split the `.gitignore`:

git rm .gitignore

cat > src/.gitignore <<'EOF'
__pycache__/
EOF

cat > src/proto_code/.gitignore <<'EOF'
/constraints.txt
/log/
/venv/
/cache/
EOF
```

```shell
# `ref_root` is now `src/proto_code/` - repoint `build_root_dir_rel_path` relative to it:

cat > src/proto_code/proto_kernel.json <<'EOF'
{
    "global_conf_dir_rel_path": ".",
    "project_descriptors": [
        {
            "build_root_dir_rel_path": "../some_app"
        }
    ]
}
EOF
```

```shell
# Regenerate `./cmd/some_app`:

./src/proto_code/proto_kernel.py wrap start_app \
    --entry_script_path "../../cmd/some_app" \
    --main_func "some_app:some_main"
```

```shell
# Commit everything:

git add --all
git commit --message "Move proto_code under ./src/proto_code/"
```

<!--- invisible-code-block: python
for rel_path in [
    "src/proto_code/proto_kernel.py",
    "src/proto_code/proto_kernel.json",
    "src/proto_code/.python-version",
    "src/proto_code/.gitignore",
    "src/.gitignore",
]:
    assert (repo_dir / rel_path).exists(), rel_path

assert not (repo_dir / "proto_kernel.py").exists()
assert not (repo_dir / ".gitignore").exists()

commit_count = subprocess.run(
    ["git", "rev-list", "--count", "HEAD"],
    cwd=repo_dir,
    capture_output=True,
    text=True,
    check=True,
).stdout.strip()
assert commit_count == "5", commit_count

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

## Dedicated entry script

We can also wrap the bootstrapper in an `entry_script` - `./prime`.

```diff
 ^/
 │
+├─ prime                                # <- dedicated entry_script for bootstrapper
 │
 ├─ cmd/
 │  │
 │  └─ some_app
 │
 ├─ src/
 │  │
 │  ├─ proto_code/
 │  │  │
 │  │  └─ ...
 │  │
 │  ├─ some_app/
 │  │  │
 │  │  └─ ...
 │  └─ ...
 └─ ...
```

<details>
<summary>[copy & paste & execute]</summary>

```shell
# Generate `./prime` with empty `main_func` as a special case to
# run the default `main_func` implemented by `protoprimer` itself:

./src/proto_code/proto_kernel.py wrap boot_env \
    --entry_script_path "../../prime" \
    --main_func ""
```

```shell
# Commit everything:

git add --all
git commit --message "Add ./prime"
```

<!--- invisible-code-block: python
prime_path = repo_dir / "prime"
assert prime_path.exists(), prime_path
assert prime_path.stat().st_mode & 0o111, "not executable"

commit_count = subprocess.run(
    ["git", "rev-list", "--count", "HEAD"],
    cwd=repo_dir,
    capture_output=True,
    text=True,
    check=True,
).stdout.strip()
assert commit_count == "6", commit_count

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

Now bootstrap via `./prime`:

```shell
./prime
```

<!--- invisible-code-block: python
prime_process = subprocess.run(
    ["./prime"],
    cwd=repo_dir,
    capture_output=True,
    text=True,
)
assert prime_process.returncode == 0, prime_process.stdout + prime_process.stderr

repo_status = subprocess.run(
    ["git", "status", "--porcelain"],
    cwd=repo_dir,
    capture_output=True,
    text=True,
    check=True,
).stdout
assert repo_status == "", repo_status

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

[FT_90_65_67_62.proto_code.md]: feature_topic/FT_90_65_67_62.proto_code.md

---

Next: [Enable updates](tutorial_enable_updates.md)
