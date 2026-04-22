
[![PyPI version](https://img.shields.io/pypi/v/protoprimer.svg?style=flat-square&color=blue&label=package)](https://pypi.org/project/protoprimer)
[![GitHub test min python job](https://img.shields.io/github/actions/workflow/status/uvsmtid/protoprimer/test_py_min.yaml.svg?style=flat-square&color=palegreen&label=py%5Bmin%5D)](https://github.com/uvsmtid/protoprimer/actions/workflows/test_py_min.yaml)
[![GitHub test med python job](https://img.shields.io/github/actions/workflow/status/uvsmtid/protoprimer/test_py_med.yaml.svg?style=flat-square&color=palegreen&label=py%5Bmed%5D)](https://github.com/uvsmtid/protoprimer/actions/workflows/test_py_med.yaml)
[![GitHub test max python job](https://img.shields.io/github/actions/workflow/status/uvsmtid/protoprimer/test_py_max.yaml.svg?style=flat-square&color=palegreen&label=py%5Bmax%5D)](https://github.com/uvsmtid/protoprimer/actions/workflows/test_py_max.yaml)
[![GitHub lint job](https://img.shields.io/github/actions/workflow/status/uvsmtid/protoprimer/lint.yaml.svg?style=flat-square&color=palegreen&label=lint)](https://github.com/uvsmtid/protoprimer/actions/workflows/lint.yaml)
[![GitHub doc job](https://img.shields.io/github/actions/workflow/status/uvsmtid/protoprimer/doc.yaml.svg?style=flat-square&color=palegreen&label=doc)](https://github.com/uvsmtid/protoprimer/actions/workflows/doc.yaml)
[![code coverage](https://img.shields.io/coveralls/github/uvsmtid/protoprimer.svg?style=flat-square&color=palegreen)](https://coveralls.io/github/uvsmtid/protoprimer)
<!--
FT_84_11_73_28.supported_python_versions.md: see above.

TODO: Use links to FC/UC docs under `./doc` (when ready) from this readme to navigate to details.
-->

# <code><a href="https://protoprimer.readthedocs.io/"><img src="doc/readthedocs/source/_static/protoprimer.logo.svg" alt="logo" style="width: 11ch; height: auto;"></a></code>

# [`protoprimer`][protoprimer_readthedocs]

Want your users to run software straight from a `git` repo with a single, zero-argument, healing command?

```sh
./prime
```

If not, see this page to double confirm:

https://protoprimer.readthedocs.io/

## Typical usage

Bootstrap (default env):

```sh
./prime
```

Bootstrap (special env):

```sh
./prime --env dst/special_env
```

Reboot: re-create venv, re-solve and re-install deps, re-pin versions:

```sh
./prime reboot
```

Evaluate the effective config:

```sh
./prime eval
```

Bootstrap into an interactive `shell` with an activated `venv`:

```sh
./cmd/venv_shell
```

See how `boot_env` works via this entry script:

```py
# ./cmd/boot_env:
# ...
proto_kernel.boot_env("local_doc.cmd_boot_env:custom_main")
```

See how `start_app` works via this entry script:

```py
# ./cmd/start_app:
# ...
proto_kernel.start_app("local_doc.cmd_start_app:custom_main")
```

<a id="protoprimer-getting-started"></a>

## Quick start

You need to "seed" your repo by a copy of the [`proto_kernel.py`][local_proto_kernel.py] script:

```mermaid
---
config:
  look: handDrawn
  theme: neutral
---
graph LR;

    install_link["**1 x install:**"]
    github_web["<br>from github.com<br>`protoprimer` repo"]

    bootstrap_link["**N x bootstrap:**"];
    pypi_web["<br>from pypi.org<br>`protoprimer` package"]

    client_repo["client repo<br>with<br>**own copy**<br>of<br>`proto_kernel.py`"];

    install_link ~~~ github_web;
    github_web --manual copy--> client_repo;

    bootstrap_link ~~~ pypi_web;
    pypi_web --auto update--> client_repo;

    style install_link fill:none,stroke:none;
    style bootstrap_link fill:none,stroke:none;
```

*   Copy (one time):

    Commit your **own copy** next to `pyproject.toml`:

    ```
    ./
    ├── proto_kernel.py    <--- own copy
    ├── pyproject.toml
    └── *
    ```

*   Run (any time):

    ```sh
    ./proto_kernel.py
    ```

*   Use a wrapper to launch `some_main` function:

    ```py
    # ./some_script.py
    # ...
    proto_kernel.start_app("some_module:some_main")
    ```

    ```sh
    ./some_script.py
    ```

*   Result:

    *   This "entry script" (wrapper) executes "proto code" by a **wild** `python` version found in `PATH`.
    *   But `some_main` is executed by the **required** `python` version inside the isolated `venv`.

*   Note:

    A shebang to `venv` (instead of "entry script") may be useless:
    *   if `venv` does not exist (during bootstrap)
    *   if `venv` has an abs path more than 128 chars
    *   if the abs path is not generated (to match every repo clone)

## What are "proto code" and "entry scripts"?

*   **"proto code"** is any code designed to be executed by arbitrary `python` version.

    The own copy of `proto_kernel.py` is most of the "proto code".

*   **"entry scripts"** are those files that rely on `proto_kernel.py` to switch to `venv`.

    Technically, "entry scripts" are also "proto code" but they only delegate.

[readme.md]: readme.md

[protoprimer_readthedocs]: https://protoprimer.readthedocs.io/

[pyapp_project]: https://github.com/ofek/pyapp

[local_proto_kernel.py]: cmd/proto_code/proto_kernel.py
[local_primer_kernel.py]: src/protoprimer/main/protoprimer/primer_kernel.py

[local_prime]: prime

[local_doc]: src/local_doc
[local_repo]: src/local_repo
[local_test]: src/local_test
[protoprimer]: src/protoprimer
[metaprimer]: src/metaprimer

[src_dir]: src
[cmd_dir]: cmd

[FT_90_65_67_62.proto_code.md]: doc/feature_topic/FT_90_65_67_62.proto_code.md
[FT_75_87_82_46.entry_script.md]: doc/feature_topic/FT_75_87_82_46.entry_script.md
[FT_57_87_94_94.bootstrap_process.md]: doc/feature_topic/FT_57_87_94_94.bootstrap_process.md

[SOLID_wiki]: https://en.wikipedia.org/wiki/SOLID
[DAG_wiki]: https://en.wikipedia.org/wiki/Directed_acyclic_graph
[make_wiki]: https://en.wikipedia.org/wiki/Make_(software)
[systemd_wiki]: https://en.wikipedia.org/wiki/Systemd

[constraints.txt]: dst/default_env/constraints.txt
[pyproject.toml]: src/metaprimer/pyproject.toml

[getting_started]: #protoprimer-getting-started

<!-- markdownlint-disable MD051 -->
<!--
NOTE: This "user-content-" prefix is added by github.com when it renders the Markdown into HTML.
-->
[shell_issues]: #user-content-shell-issues
<!-- markdownlint-enable -->
