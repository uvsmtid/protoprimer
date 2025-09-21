
[![lifecycle: experimental](https://img.shields.io/badge/lifecycle-experimental-purple.svg?color=purple)](https://github.com/uvsmtid/protoprimer)
[![PyPI version](https://img.shields.io/pypi/v/protoprimer.svg?color=blue&label=package)](https://pypi.org/project/protoprimer)
[![GitHub test job](https://img.shields.io/github/actions/workflow/status/uvsmtid/protoprimer/test.yaml.svg?label=test)](https://github.com/uvsmtid/protoprimer/actions/workflows/test.yaml)
[![GitHub lint job](https://img.shields.io/github/actions/workflow/status/uvsmtid/protoprimer/lint.yaml.svg?label=lint)](https://github.com/uvsmtid/protoprimer/actions/workflows/lint.yaml)
[![code coverage](https://img.shields.io/coveralls/github/uvsmtid/protoprimer.svg?color=brightgreen)](https://coveralls.io/github/uvsmtid/protoprimer)
<!--
TODO: nothing to show:
[![contributors](https://img.shields.io/github/contributors/uvsmtid/protoprimer.svg?color=white)](https://github.com/uvsmtid/protoprimer/graphs/contributors)
TODO: not accessible anymore:
[![PyPI downloads](https://img.shields.io/pypi/dm/protoprimer.svg?color=blue)](https://pypi.org/project/protoprimer)
-->

# `protoprimer`

## TL;DR

Every time people clone some `repo.git`,\
they may have to prepare/bootstrap/prime the repo,\
ideally, using one-step no-arg command:

```sh
./prime
```

To use `python`, the `protoprimer` solves the "chicken & egg" problem\
of running `venv`-dependent user code when `venv` is not ready.

As a byproduct, it enables direct pure `python` execution by\
avoiding intermediate (non-test-able, less readable, error-prone) shell scripts.

## Why `proto*`?

`proto` = early, when nothing exists yet.

The `protoprimer` design aims to survive with **minimal pre-conditions**:

*   no dependencies pre-installed on the system
*   no `venv` pre-initialized with specific `python` version
*   no args for the user to understand
*   no special shell config
*   ...
*   just naked `python` (relatively omnipresent) + [a stand-alone copy][FT_90_65_67_62.proto_code.md] of the `protoprimer`.

## How to install it?

Commit the entire content of [`proto_kernel.py`][local_proto_kernel.py] into the target client repo\
(to be immediately available on repo clone).

Then, try:

```sh
./proto_kernel.py -h
```

The script is stand-alone, but it auto-updates itself from the `protoprimer` package when `venv` is ready.

## How to tell it what to do?

It is configurable (one-time):

```sh
./proto_kernel.py --wizard
```

The generated configuration is reused in all the subsequent repo clones.

## How does it work?

The entire repo is centered around the single [primer_kernel.py][primer_kernel.py] file.

It uses an extensible [DAG][DAG_wiki] to boostrap a specific state with all its dependencies.

For example,\
[`./prime`][local_prime] (a dummy proxy) relies on\
[`proto_kernel.py`][local_proto_kernel.py] (a local stand-alone copy)\
which:
*   first, bootstraps the environment via itself (outside `venv`),
*   then, continues to bootstrap it via `protoprimer.primer_kernel` (inside `venv`)
*   auto-updates the copy within the client repo (to be available on repo clone)
*   eventually passes control back to trigger additional client-specific steps

See details on the [bootstrap process][FT_57_87_94_94.bootstrap_process.md].

<!--
## How to extend and customize it?

TODO

-->

## What are the primary features?

Early steps run in **very inconvenient conditions**, but they are also **very common and very boring**:

*   distinguish (A) global repo-wide and (B) local environment-specific configuration
*   respect a flexible repo filesystem layout (choices made by the target client repo)
*   init `venv`, install the necessary dependency, pin versions
*   switch initial arbitrary OS-picked `python` binary to the required version
*   delegate to client-specific modules to do the rest (**more interesting stuff**)

Roughly:
*   pre-`venv` runtime is the scope of `protoprimer`
*   post-`venv` runtime is the scope of `neoprimer`

## Directory structure

Each subdirectory of [src][src] directory contains related subprojects (with corresponding `pyproject.toml`):
*   [protoprimer][protoprimer] is the main project that addresses running Python code before `venv` is fully configured
*   [neoprimer][neoprimer] contains extensions with code useful run after `venv` is fully configured
*   [local_repo][local_repo] hosts various non-release-able support scripts for this repo
*   [local_test][local_test] provides non-release-able test help code

---

[primer_kernel.py]: src/protoprimer/main/protoprimer/primer_kernel.py
[proto_kernel.py]: cmd/proto_code/proto_kernel.py

[local_repo]: src/local_repo
[local_test]: src/local_test
[protoprimer]: src/protoprimer
[neoprimer]: src/neoprimer

[src]: src
[cmd]: cmd

[readme.md]: readme.md
[local_proto_kernel.py]: src/protoprimer/main/protoprimer/primer_kernel.py
[local_prime]: prime
[original_motivation.md]: doc/dev_note/original_motivation.md
[FT_90_65_67_62.proto_code.md]: doc/feature_topic/FT_90_65_67_62.proto_code.md
[SOLID_wiki]: https://en.wikipedia.org/wiki/SOLID
[DAG_wiki]: https://en.wikipedia.org/wiki/Directed_acyclic_graph
[make_wiki]: https://en.wikipedia.org/wiki/Make_(software)
[systemd_wiki]: https://en.wikipedia.org/wiki/Systemd
[FT_57_87_94_94.bootstrap_process.md]: doc/feature_topic/FT_57_87_94_94.bootstrap_process.md
