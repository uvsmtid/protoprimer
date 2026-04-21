```{eval-rst}
.. meta::
   :description: ``protoprimer`` is an arg-less ``python`` one-liner to bootstrap a ``venv`` for repo clones
   :keywords: bootstrap, venv, install, python, required, version
```

# [![logo](/_static/protoprimer.logo.16x16.png)][protoprimer_github] [`protoprimer`][protoprimer_github]

```{include} /full/01_basic/01_intro.md
:start-after: stub_include_start
:end-before: stub_include_stop
```

## Why?

More than one manual step is **tedious and error-prone**.

Plus, the **single-step** bootstrap is a non-trivial "chicken and egg" problem!

<details class="indented">
<summary>[formal proof]</summary>

<details class="indented">

<summary>0. You may have a project in any lang.</summary>

> C++, Java, Go, JS/TS, Rust, Haskell, ...

**Next:** you may still need to automate with something else...

</details>

<details class="indented">

<summary>1. <em>"What is the <strong>best</strong> glue for automation, if not <code>python</code>?"</em></summary>

*   readable, testable, modular, cross-platform, ...
*   huge mind-share, gazillion of packages, ...

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

**Next:** `uv` reproduces `venv`, but steps may go **beyond** that.

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

the lang has to be:
*   cross-platform
*   ubiquitous (like `shell`)
*   require no explicit compilation

**Next:** you are in a cycle back to **point 1** for `python`.

</details>

You need to break that 5-to-1 loop.

</details>

The entry script must **evolve through chaos** to survive.

In other words, it must become **both** "the chicken **and** the egg".

## How?

```{include} /full/02_advanced/03_implementation.md
:start-after: stub_include_start
:end-before: stub_include_stop
```

<!--

TODO: Move those sections into main `readme.md`, itemize them with links to `FC_` docs (`fature_topic`-s).

## Details

```{include} /full/02_advanced/01_solutions.md
:start-after: stub_include_start
:end-before: stub_include_stop
```

-->

<div style="text-align: center; margin-top: 8em; margin-bottom: 8em;">

[View on GitHub][protoprimer_github]

</div>

<!--

TODO: Put it somewhere: or is it already obvious?

## Why `proto*`?

`proto` = early, when nothing exists yet.

`protoprimer` design aims to survive with **minimal pre-conditions**:

*   no pre-installed dependencies
*   no pre-initialized `venv`
*   no required `python` version in `PATH`
*   no special shell config
*   no user CLI args to guess (by default)
*   ...
*   just naked `python` (relatively omnipresent) + [a stand-alone copy][FT_90_65_67_62.proto_code.md] of `protoprimer`.

##

Those early bootstrap steps:
*   distinguish (A) global repo-wide and (B) local environment-specific configuration
*   office-friendly: supporting limited permissions, mirrors for package indexes, proxies, etc.
*   respect flexible repo filesystem layouts - from min to max (choices made by the target client repo)
*   init `venv`, install the necessary dependencies, pin package versions
*   switch initial arbitrary OS-picked `python` binary from the `PATH` to the required version
*   propagate param overrides: config fields - env vars - CLI args
*   delegate to client-specific modules to do the rest\
    (**to run more interesting stuff**)

</details>

-->

[protoprimer_github]: https://github.com/uvsmtid/protoprimer
