```{eval-rst}
.. meta::
   :description: ``protoprimer`` is an arg-less ``python`` one-liner to bootstrap a ``venv`` for repo clones
   :keywords: bootstrap, venv, install, python, required, version
```

# [![logo](/_static/protoprimer.logo.16x16.png)][protoprimer_github] [`protoprimer`][protoprimer_github]

Do not write manuals. Instead:

```sh
./prime
# your repo clone
```

`protoprimer` provides **arg-less** stand-alone **idempotent** bootstrap code that transitions:

*   from **chaos** (the many conditions in which a user may invoke it)
*   into **order** (an env-specific `venv` with the **required** `python` version)

It handles messy init details, then it **hands off control** to user code in:

<details>
<summary>[guaranteed environment]</summary>

*   As a **bootstrapper**, `protoprimer` lets custom steps prepare **anything** else:

    *   install `git` hooks

    *   provision other SDKs

    *   build required dependencies from sources

    *   assert system and user config

    *   download env-specific data

    *   generate env-specific code

    *   verify authn and authz prerequisites

    *   ... [you name it]

*   As a **starter**, `protoprimer` invokes a specified custom function from `venv`.

</details>

## Python?

It has to be `python` to run **right off the bootstrap**:

<details>
<summary>[have no doubts]</summary>

*   ubiquitous: **any** `python` is a **trivial** requirement to satisfy
*   script (**text**, not binary): hosted in user repos, providing audit and security
*   **no** compilation: immediately runnable on the command line after a change
*   **rich** core SDK: zero dependencies to be useful
*   cross-platform: avoids excessive branching
*   vast mind-share: easily maintainable
*   ...

</details>

User code may prepare to [run **anything** else][pypl_index].

## When?

When you **avoid conflicting system-wide changes**.

When you want direct execution:

*   to bootstrap an **isolated** repo clone environment with a **one-liner**:

    ```sh
    ./boot_env
    ```

*   to start an **isolated** app from **co-existing** repo clones at **different versions**:

    ```sh
    ./start_app
    ```

## Why?

Everyone likes a **single reproducible step** to run anything - an end-to-end command.

<details>
<summary>[imagine otherwise]</summary>

Multiple manual steps are **tedious and error-prone**:
*   **users**, and repo **clones** they maintain, **multiply**
*   subsequent update **avalanches** into re-execution of steps
*   environment conditions **interfere with** the sequence of steps
*   partial failures, re-ordering, mistakes, ... turn into **a support nightmare**
*   LLMs fix that with **increased complexity**, wasting more time and money

</details>

<!-- markdownlint-disable-next-line MD026 -->
## Cases:

Replacing **untested** non-modular init `shell` scripts with **pure** `python` requires:

<details>
<summary>[robust initialization]</summary>

*   Bootstrapping a cloned repo (local or cloud) to run stuff from it.
*   Preparing a continuous integration job (after cloning a repo).
*   Spinning up a container from a minimal base image.
*   ...

</details>

<!-- markdownlint-disable-next-line MD026 -->
## But...

The **single-step** bootstrap is a **non-trivial** "chicken and egg" problem!

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

## How?

`protoprimer` **iteratively restarts** to prepare the environment:

*   Takes off with a **wild** `python` version (whatever is in the `PATH` env var).

*   Switches in-flight to the **required** `python` version.

*   Satisfies a set of DAG-organized pre-conditions on each restart cycle.

*   Lands inside a comfy isolated `venv` with all dependencies **pinned**.

    > The user code **takes over** here.

<!-- markdownlint-disable-next-line MD026 -->
## Specifically...

User repo hosts [proto_kernel.py][proto_kernel] - the single script that **survives**:

<details>
<summary>[minimal pre-conditions]</summary>

*   only naked `python` of **unpredictable version** in `PATH`
*   **no** pre-installed dependencies (ignored if any)
*   **no** pre-activated `venv` (ignored if any)
*   **no** special `shell` config
*   **no** user CLI args (by default)
*   ...

</details>

User configures it to prepare:

<details>
<summary>[target environment]</summary>

*   navigate the user repo directory structure to discover config and packages
*   handle global (repo-wide) and local (environment-specific) config
*   provide authn and authz for internal artifact repositories
*   use "editable install" for local packages
*   switch to required `python` version
*   execute user-specific code
*   ...

</details>

<div style="text-align: center; margin-top: 8em; margin-bottom: 8em;">

Poke your LLM to see where it fits...

</div>

[protoprimer_github]: https://github.com/uvsmtid/protoprimer
[pypl_index]: https://pypl.github.io/
[proto_kernel]: https://github.com/uvsmtid/protoprimer/blob/main/src/proto_code/proto_kernel.py
