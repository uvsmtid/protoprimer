
[![PyPI package](https://badge.fury.io/py/protoprimer.svg)](https://pypi.org/project/protoprimer)
[![GitHub build](https://github.com/uvsmtid/protoprimer/actions/workflows/protoprimer.test.yaml/badge.svg?branch=main)](https://github.com/uvsmtid/protoprimer/actions/workflows/protoprimer.test.yaml)


# `protoprimer`

## TL;DR

`protoprimer`:

*   bootstraps target dev environment
*   is a self-contained script (has no dependencies)
*   is copied and tracked within a client repo (with self-auto-updates)
*   provides a [SOLID][SOLID_wiki]-extensible framework to pull a specific state with all its [DAG][DAG_wiki] of dependencies

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
*   gradually executes bootstrap, first, via itself (standalone), then, via `protoprimer.primer_kernel` (in `venv`)
*   eventually passes control back to `./cmd/bootstrap_env` which triggers additional steps

`protoprimer` is done when:
1.  required `python` version is running
2.  `vevn` is activated
3.  all `python` packages are installed
4.  environment-specific configuration is effective
5.  client-specific code can take over

## Why **not** ad-hoc bootstrap scripts instead?

This has been re-invented multiple times by everyone, but...

The combination of the following features makes such scripts rather complex to re-invent:

*   keep implementation sane under growing requirements
*   support for empty or partially initialized environment
*   support starting with any python version then switching to desired `python` version
*   support for multiple target environments (with its environment-specific config)
*   support for generated config and code (to avoid boilerplate)
*   support for param overrides: client-wide → environment-specific → command line arg
*   testability (isolated test executions with standard frameworks in IDE)
*   ~~one-liner~~ one-"worder" (simple to use without pre-conditions): `./bootstrap`

<!--
Add the point (when ready): it is possible to start with simple and move to complex setup gradually.
-->

---

[readme.md]: readme.md
[SOLID_wiki]: https://en.wikipedia.org/wiki/SOLID
[DAG_wiki]: https://en.wikipedia.org/wiki/Directed_acyclic_graph
