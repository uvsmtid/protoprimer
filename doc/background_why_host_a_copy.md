```{eval-rst}
.. meta::
   :description: Why `protoprimer` is hosted as a copy in the user repo: the single-step bootstrap is a chicken and egg problem
   :keywords: background, reuse, bootstrap, one-liner, chicken and egg, repo clone
```

# Why host a copy?

Distributing software via repo clones has its benefits:
*   instant updates in both directions (push or pull)
*   comprehensive LLM support

Everyone likes a **single reproducible step** to run anything - an end-to-end command.

<details>
<summary>[imagine otherwise]</summary>

Multiple manual steps are **tedious and error-prone**:
*   **users**, and repo **clones** they maintain, **multiply**
*   subsequent update **avalanches** into re-execution of steps
*   the sequence of steps **depends** on the environment state
*   **non-isolated** repo clones conflict in dependency versions
*   partial failures, re-ordering, mistakes, ... turn into **a support nightmare**

</details>

## Problem: chicken and egg

But how do we reuse it without making the user install it first?

The **single-step** bootstrap is a **non-trivial** problem:

<details class="indented">
<summary>["formal" proof]</summary>

<details class="indented">

<summary>0. You may have a project in any lang.</summary>

> C++, Java, Go, JS/TS, Rust, Haskell, ...

**Next:** you may still need to automate with something else...

</details>

<details class="indented">

<summary>1. <em>"What is the <strong>best</strong> glue for automation, if not <code>python</code>?"</em></summary>

*   readable, testable, modular, cross-platform, ...
*   vast mind-share, a gazillion packages, ...

**Next:** you need an isolated `venv` for dependencies.

</details>

<details class="indented">
<summary>2. <em>"I can <strong>manage</strong> a <code>venv</code> everywhere"</em></summary>

*   that `venv` has to be created by **every** user
*   **everyone** has to `activate` it **every** time

**Next:** you need to ensure the **required** `python` for `venv` creation.

</details>

<details class="indented">
<summary>3. <em>"I can use <code>uv</code> to ensure the <strong>required</strong> <code>python</code> version"</em></summary>

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
<summary>4. <em>"I can <strong>wrap</strong> it all into a <code>shell</code> script"</em></summary>

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
<summary>5. <em>"I can replace <code>shell</code> with a <strong>better</strong> lang, but which one?"</em></summary>

The lang has to be:
*   cross-platform
*   ubiquitous (like `shell`)
*   compilation-free

**Next:** you are in a cycle back to **point 1** for `python`.

</details>

You need to break that 5-to-1 loop.

</details>

The entry script has to **dynamically evolve** with the environment it builds step-by-step.

## Solution: host a copy

The entire `protoprimer` code (its auto-update-able copy) is committed to the user repo.

It is an immediately runnable `python` code requiring no `venv`.
