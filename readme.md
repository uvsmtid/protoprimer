
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

*   Let's say you have a `repo.git`.

*   Every time people clone it, before they can do anything,\
    they have to prepare/bootstrap/prime the repo.

    You want a one-step no-arg command to prime the repo clone:

    ```sh
    ./prime
    ```

As a byproduct, it facilitates pure `python` automation irradicating (non-test-able & unreadable) shell scripts.

## Why `proto*`?

`proto` = early, when nothing exists yet.

The `protoprimer` design aims to survive with **minimal pre-conditions**:

*   no dependencies pre-installed on the system
*   no `venv` pre-initialized with specific `python` version
*   no args for the user to understand
*   no special shell config
*   ...
*   just naked `python` (relatively omnipresent) + [a stand-alone copy][FT_90_65_67_62.proto_code.md] of the `protoprimer`.

## How does it know what to do?

It is configurable (once):

```sh
./prime --wizard
```

The generated configuration is versioned and reused on the repo clone.

Early steps run in **very inconvenient conditions**, but they are also **very common and very boring**:

*   find all the target environment configurations in a flexible repo filesystem layout
*   init `venv` and install the necessary dependency
*   switch from initial `python` binary to the `venv` version required by configuration
*   capture the env state to keep it reproducible
*   delegate to client-specific modules to do the rest (**more interesting stuff**)

That is the scope of the `protoprimer`.

## How to install it?

Commit [`proto_kernel.py`][local_proto_kernel.py] into the target client repo\
(to be immediately available on repo clone).

Then, try:

```
python ./proto_kernel.py -h
```

The script is stand-alone, but it auto-updates itself from `protoprimer` package when `venv` is ready.

This is what [`./prime`][local_prime] delegates execution to, for example.

## How does it work?

For example, [`./prime`][local_prime] (a dummy proxy) relies on `./cmd/proto_kernel.py` (a copy) which, in turn:
*   bootstraps the environment, first, via itself (standalone), then, via `protoprimer.primer_kernel` (in `venv`)
*   auto-updates its copy within the client repo (to be available on repo clone)
*   provides a [SOLID][SOLID_wiki]-extensible framework to pull a specific state with all its [DAG][DAG_wiki] of dependencies
*   eventually passes control back to [`./prime`][local_prime] which may trigger additional client-specific steps

See details on the [bootstrap process][FT_57_87_94_94.bootstrap_process.md].

<!--
## How to extend and customize it?

TODO

-->

## Similarities & Differences

Anyone who knows [`make`][make_wiki], or [`systemd`][systemd_wiki], ...
(or other tools to bootstrap an environment to the target state) will find `protoprimer` similar.

What makes `protoprimer` different:
*   limited scope: early initialization in less predictable (dev) environments
*   pure `python`: all state dependencies, trigger conditions, build instructions, custom extensions, ...

---

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
