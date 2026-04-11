```{eval-rst}
.. meta::
   :description: ``protoprimer`` is an arg-less ``python`` one-liner to bootstrap a ``venv`` for repo clones
   :keywords: bootstrap, venv, install, python, required, version
```

# [`protoprimer`][protoprimer_github]

```{include} /full/01_basic/01_intro.md
:start-after: stub_include_start
:end-before: stub_include_stop
```

## Why?

Because more than one step is an **error-prone boring manual**.

<details class="indented">
<summary>This is a non-trivial "chicken and egg" problem:</summary>

<br/>

<details>

<summary>0. You may have a project in any lang:</summary>

> C++, Java, Go, *Script, Rust, Haskel, ...

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
*   **everyone** has to be exposed to `uv` args like:

```bash
uv pip install --editable path/to/project_1
uv pip install --editable path/to/project_2
...
```

**Next:** this is just the tip of the iceberg you may want to automate away.

</details>

<details>
<summary>4. Thought: <em>"I can wrap all into a <code>shell</code>-script"</em></summary>

*   to distinguish an initial bootstrap from a subsequent update
*   to load env-specific configuration

**Next:** `shell` is untestable, non-modular, platform-dependent, cryptic, ...

</details>

<details>
<summary>5. Thought: <em>"I can avoid <strong>unpredictable</strong> <code>shell</code> with another lang"</em></summary>

*   the lang has to be cross-platform
*   the lang has to be as ubiquitous as `shell` (even more)

**Next:** you are in a cycle back to **point 1** for `python`.

</details>

You need to break that 5-to-1 loop.

</details>

An entry script must **handle unpredictable conditions** to solve that.

## How?

```{include} /full/02_advanced/03_implementation.md
:start-after: stub_include_start
:end-before: stub_include_stop
```

## Quick dive

```{include} /full/02_advanced/01_solutions.md
:start-after: stub_include_start
:end-before: stub_include_stop
```

[protoprimer_github]: https://github.com/uvsmtid/protoprimer
