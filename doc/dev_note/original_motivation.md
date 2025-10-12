
# Original motivation

## When to use it?

*   you need a command to bootstrap `venv` (for users of your project) with dependencies, generate config, etc.
*   the command has to require **no args** and has no pre-conditions by default
*   you do not want to "re-invent the wheel" for extra requirements with flexible configuration

## Why **not** ad-hoc bootstrap script instead?

The combination of the following features **makes such scripts rather complex to re-invent**:

*   keep implementation sane under growing requirements: start with simple and move to complex setup gradually
*   support for empty or partially initialized environment
*   support starting with any python version then switching to desired `python` version
*   support for multiple target environments (with its environment-specific config)
*   support for generated config and code (to avoid boilerplate)
*   support for param overrides: client-wide → environment-specific → command line arg
*   testability (isolated test executions with standard frameworks in IDE)

## Why **not** shell script instead?

Because shell scripts:

*   are not test-able (there is no such practice)
*   are cryptic, full of special cases, and allow unpredictable user overrides
*   have no stack traces on failure (often leading to excessive logging to compensate for that)

[All these and more][FT_44_72_60_67.python_vs_shell.md] made `protoprimer` "allow `python`-only scripts" its secondary objective.

---

[readme.md]: original_motivation.md
[SOLID_wiki]: https://en.wikipedia.org/wiki/SOLID
[DAG_wiki]: https://en.wikipedia.org/wiki/Directed_acyclic_graph
[FT_44_72_60_67.python_vs_shell.md]: ../feature_topic/FT_44_72_60_67.python_vs_shell.md
[FT_57_87_94_94.bootstrap_process.md]: ../feature_topic/FT_57_87_94_94.bootstrap_process.md
