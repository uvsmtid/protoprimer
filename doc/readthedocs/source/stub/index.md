```{eval-rst}
.. meta::
   :description: ``protoprimer`` is an arg-less ``python`` one-liner to bootstrap a ``venv`` for repo clones
   :keywords: bootstrap, venv, install, python, required, version
```

# ![logo](/_static/protoprimer.logo.16x16.png) [`protoprimer`][protoprimer_github]

```{include} /full/01_basic/01_intro.md
:start-after: stub_include_start
:end-before: stub_include_stop
```

## Why?

More than one manual step is **tedious and error-prone**.

<details class="indented">
<summary>Yet achieving the <strong>single-step</strong> bootstrap is a "chicken and egg" problem:</summary>

<br/>

<details>

<summary>0. Premise: You may have a project in any lang.</summary>

> C++, Java, Go, JS/TS, Rust, Haskell, ...

**Next:** you may still need to automate with something else...

</details>

<br/>

<details>
<summary>1. Thought: <em>"What is the best glue for automation, if not <code>python</code>?"</em></summary>

*   readable, testable, modular, cross-platform, ...
*   huge mind-share, gazillion of packages, ...

**Next:** you need an isolated `venv` for dependencies.

</details>

<details>
<summary>2. Thought: <em>"I can create a <code>venv</code> manually"</em></summary>

*   that `venv` has to be created by **every** user
*   **everyone** has to `activate` it **every** time

**Next:** you need to ensure the **required** `python` for `venv` creation.

</details>

<details>
<summary>3. Thought: <em>"I can use <code>uv</code> to ensure the <strong>required</strong> <code>python</code> version"</em></summary>

*   **everyone** has to install the `uv` executable first
*   **everyone** has to know `uv` args like:

```bash
uv pip install --editable path/to/project_1
uv pip install --editable path/to/project_2
...
```

**Next:** `uv` reproduces `venv`, but steps may go beyond that scope.

</details>

<details>
<summary>4. Thought: <em>"I can wrap it all into a <code>shell</code>-script"</em></summary>

This demands logic to handle flexibility:

*   to load env-specific configuration and respect it
*   to distinguish an initial bootstrap from a subsequent update

**Next:** `shell` is:
*   untestable
*   non-modular
*   platform-dependent
*   cryptic
*   ...

</details>

<details>
<summary>5. Thought: <em>"I can avoid <strong>inconvenient</strong> <code>shell</code> with another lang"</em></summary>

the lang has to be:
*   cross-platform
*   ubiquitous (like `shell`)
*   require no explicit compilation

**Next:** you are in a cycle back to **point 1** for `python`.

</details>

You need to break that 5-to-1 loop.

</details>

The entry script must **self-handle early chaotic conditions**.

In other words, it must become **both** "the chicken **and** the egg".

## How?

```{include} /full/02_advanced/03_implementation.md
:start-after: stub_include_start
:end-before: stub_include_stop
```

## Flexibility

The iterative restart handles initial conditions for all:

*   a **single-package repo** with a lone library

*   a **multi-lang monorepo** with arbitrary directory structure

## Use cases

You can:

*   **Bootstrap an environment:**

    This case is the most involved and the main focus for `protoprimer`.

    Everything discussed so far relates to bootstrapping.

    % See FT_85_17_35_21.boot_env.md

*   **Start an application:**

    This case is used to start applications without explicit `venv` activation.

    The goal is also to avoid the 128-char shebang length limit.

    % See FT_05_08_64_67.start_app.md

## Details

```{include} /full/02_advanced/01_solutions.md
:start-after: stub_include_start
:end-before: stub_include_stop
```

<div style="text-align: center; margin-top: 8em; margin-bottom: 8em;">

[View on GitHub][protoprimer_github]

</div>

[protoprimer_github]: https://github.com/uvsmtid/protoprimer
