```{eval-rst}
.. meta::
   :description: Why `protoprimer` starts as immediately runnable `python` code: a single-step bootstrap is a chicken and egg problem
   :keywords: background, proto, bootstrap, python, venv, chicken and egg
```

# Why proto?

The Greek word "proto" means "first", "early", "initial", ...

The **single-step** pure `python` bootstrap is a **non-trivial** "chicken and egg" problem:
*   first, a **wild** `python` version has to run to obtain the **required** `python` version
*   then, the **required** `python` version starts to provide versioned dependencies
*   ...

Consider:

<details class="indented">
<summary>["formal" proof]</summary>

<details class="indented">

<summary>0. You may have a project in any lang.</summary>

> C++, Java, Go, JS/TS, Rust, Haskell, ...

**Next:** you may still need to automate with something else...

</details>

<details class="indented">

<summary>1. <em>"But what to pick for automation, if not <code>python</code>?"</em></summary>

*   readable, testable, modular, cross-platform, ...
*   vast mind-share, a gazillion packages, ...

**Next:** you need an isolated `venv` for dependencies.

</details>

<details class="indented">
<summary>2. <em>"I can <strong>manage</strong> a <code>venv</code> everywhere."</em></summary>

*   that `venv` has to be created by **every** user
*   **everyone** has to `activate` it **every** time

**Next:** you need to ensure the **required** `python` for `venv` creation.

</details>

<details class="indented">
<summary>3. <em>"I can use <code>uv</code> to ensure the <strong>required</strong> <code>python</code> version."</em></summary>

*   **everyone** has to install the `uv` executable first
*   **everyone** has to know `uv` args like:

```bash
uv pip install --editable path/to/project_1
uv pip install --editable path/to/project_2
...
```

**Next:** `uv` reproduces any `venv`, but steps may go **beyond** that.

</details>

<details class="indented">
<summary>4. <em>"I can <strong>wrap</strong> it all into a <code>shell</code> script."</em></summary>

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

<details class="indented">
<summary>5. <em>"I can replace <code>shell</code> with a <strong>better</strong> lang."</em></summary>

The lang has to be:
*   cross-platform
*   ubiquitous (like `shell`)
*   compilation-free

**Next:** you are in a cycle back to **point 1** for `python`.

</details>

You need to break that 5-to-1 loop.

</details>

## Problem: **pushing** the "chicken and egg" problem

The (early, first) proto stages of pre-`venv` preparation can be done:
*   using `shell` - see: [Why not `shell`?][background_why_not_shell.md]
*   using another pre-installed tool or a manual - see: [Alternative][doc_alternative].
*   ...

But that would be pushing the problem somewhere else.

A pre-installed **wild** `python` is almost everywhere - why not use it instead?

## Solution: **facing** the "chicken and egg" problem

The approach is to run `python` immediately in one shot but split the runtimes (roughly):
*   pre-`venv`
*   post-`venv`
*   user code

`protoprimer` uses pure `python` to run the initial steps requiring no `venv`.

It is designed to survive chaos, running even in ancient `python` versions.

The runtime **evolves dynamically** with the environment `protoprimer` builds step-by-step.

[background_why_not_shell.md]: background_why_not_shell.md
[doc_alternative]: alternative.md
