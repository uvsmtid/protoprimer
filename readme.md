
[![PyPI package](https://badge.fury.io/py/protoprimer.svg)](https://pypi.org/project/protoprimer)
[![GitHub test](https://github.com/uvsmtid/protoprimer/actions/workflows/protoprimer.test.yaml/badge.svg?branch=main)](https://github.com/uvsmtid/protoprimer/actions/workflows/protoprimer.test.yaml)
[![GitHub lint](https://github.com/uvsmtid/protoprimer/actions/workflows/protoprimer.lint.yaml/badge.svg?branch=main)](https://github.com/uvsmtid/protoprimer/actions/workflows/protoprimer.lint.yaml)
[![Coverage](https://coveralls.io/repos/github/uvsmtid/protoprimer/badge.svg?branch=main)](https://coveralls.io/github/uvsmtid/protoprimer)

# `protoprimer`

## TL;DR

*   Let's say you have a `repo.git`.
*   Let's say everyone has to prepare/init/bootstrap/prime the repo\
    (after they clone, before they do anything).
*   That's exactly what `protoprimer` does -\
    it provides the script for everyone to run after the repo clone:

    ```sh
    ./prime
    ```

## Why `proto*`?

`protoprimer` design aims to survive with **minimal pre-conditions**:

*   no dependencies pre-installed on the system
*   no `venv` pre-initialized via extra instructions
*   no args to document for user consumption
*   no special shell config
*   ...
*   just naked `python` (relatively omnipresent) + a stand-alone copy of [proto_kernel][FT_90_65_67_62.proto_kernel.md].

`proto` = early, when nothing is born yet.

## How does `*primer` knows what other repos want?

Early steps are very common and very boring (which is the [original_motivation][original_motivation.md] not to do it again):

*   switch from initial `python` binary to the version required by configuration
*   init `venv` and install the necessary dependency
*   switch `python` again to the one provided by the fresh `venv`
*   capture the state to keep it reproducible

Early steps are also well-scoped and customize-able (they grow with the repo complexity but have the limit):

*   override defaults by those configured for target environment
*   support flexible repo filesystem layout
*   delegate to client-specific modules to do the rest (**more interesting stuff**)

In short, the `primer`'s boring job is done in the early **inconvenient conditions** before anything else can start.

## How does it work?

For example, `./prime` (a dummy proxy) relies on `./cmd/proto_kernel.py` which, in turn:
*   bootstraps the environment, first, via itself (standalone), then, via `protoprimer.primer_kernel` (in `venv`)
*   auto-updates its copy within the client repo (to be available on repo clone)
*   provides a [SOLID][SOLID_wiki]-extensible framework to pull a specific state with all its [DAG][DAG_wiki] of dependencies
*   eventually passes control back to `./prime` which may trigger additional client-specific steps

See details on the [bootstrap process][FT_57_87_94_94.bootstrap_process.md].

## Does it look familiar?

Anyone who knows [`make`][make_wiki], or [`systemd`][systemd_wiki], ...
(or other tools to bootstrap an environment to the target state) will find `protoprimer` similar.

What makes `protoprimer` different:
*   its scope: early initialization in less predictable (dev) environments
*   pure `python`: all state dependencies, trigger conditions, build instructions, custom extensions, ...

---

[readme.md]: readme.md
[original_motivation.md]: doc/dev_note/original_motivation.md
[FT_90_65_67_62.proto_kernel.md]: doc/feature_topic/FT_90_65_67_62.proto_kernel.md
[SOLID_wiki]: https://en.wikipedia.org/wiki/SOLID
[DAG_wiki]: https://en.wikipedia.org/wiki/Directed_acyclic_graph
[make_wiki]: https://en.wikipedia.org/wiki/Make_(software)
[systemd_wiki]: https://en.wikipedia.org/wiki/Systemd
[FT_57_87_94_94.bootstrap_process.md]: doc/feature_topic/FT_57_87_94_94.bootstrap_process.md
