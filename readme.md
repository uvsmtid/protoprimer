
[![PyPI package](https://badge.fury.io/py/protoprimer.svg)](https://pypi.org/project/protoprimer)
[![GitHub build](https://github.com/uvsmtid/protoprimer/actions/workflows/protoprimer.test.yaml/badge.svg?branch=main)](https://github.com/uvsmtid/protoprimer/actions/workflows/protoprimer.test.yaml)
[![GitHub build](https://github.com/uvsmtid/protoprimer/actions/workflows/protoprimer.lint.yaml/badge.svg?branch=main)](https://github.com/uvsmtid/protoprimer/actions/workflows/protoprimer.lint.yaml)

# `protoprimer` ~ bootstrapper from nothing

## TL;DR: What does it do?

*   bootstraps target environment
*   stays a self-contained script (has no dependencies)
*   has an auto-updated tracked copy of itself within a client repo (to be available on repo clone)
*   provides a [SOLID][SOLID_wiki]-extensible framework to pull a specific state with all its [DAG][DAG_wiki] of dependencies

## When to use it?

*   you need a command to boostrap `venv` (for users of your project)
*   the command has to require **no args** and no pre-conditions by default
*   you do not want to "re-invent the wheel" for extra requirements with flexible configuration
*   (especially) you do not want to rely on messy (untestable) shell scripts and use pure `python` instead

## How to try it?

`protoprimer` uses itself to bootstrap itself.

To try, (re-)run this (any time):

```sh
./cmd/bootstrap_env
```

## How does it work?

The bootstrap process relies on the copy of `protoprimer.primer_kernel` module saved as a self-contained script:

```sh
./cmd/proto_kernel.py
```

In this case `./cmd/bootstrap_env` (a dummy proxy) relies on `./cmd/proto_kernel.py` which, in turn:
*   bootstraps the environment, first, via itself (standalone), then, via `protoprimer.primer_kernel` (in `venv`)
*   eventually passes control back to `./cmd/bootstrap_env` which may trigger additional client-specific steps

`protoprimer` is done when:
1.  required `python` version is running
2.  `venv` is activated
3.  required packages are installed
4.  environment-specific configuration is effective
5.  client-specific code takes over

## Why **not** ad-hoc bootstrap script instead?

The combination of the following features makes such scripts rather complex to re-invent:

*   keep implementation sane under growing requirements
*   support for empty or partially initialized environment
*   support starting with any python version then switching to desired `python` version
*   support for multiple target environments (with its environment-specific config)
*   support for generated config and code (to avoid boilerplate)
*   support for param overrides: client-wide → environment-specific → command line arg
*   testability (isolated test executions with standard frameworks in IDE)

<!--
Add the point (when ready): it is possible to start with simple and move to complex setup gradually.
-->

## Why **not** shell script instead?

Because shell scripts:

*   are not test-able (there is no such practice)
*   are cryptic, full of special cases, and allow unpredictable user overrides
*   have no stack traces on failure (often leading to excessive logging)

[All these and more][FS_44_72_60_67.python_vs_shell.md] made `protoprimer` "allow `python`-only scripts" its secondary objective.

---

[readme.md]: readme.md
[SOLID_wiki]: https://en.wikipedia.org/wiki/SOLID
[DAG_wiki]: https://en.wikipedia.org/wiki/Directed_acyclic_graph
[FS_44_72_60_67.python_vs_shell.md]: doc/FS_44_72_60_67.python_vs_shell.md
