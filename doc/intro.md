```{eval-rst}
.. meta::
   :description: `protoprimer` is an arg-less one-liner to bootstrap isolated repo clones with environment-specific config
   :keywords: protoprimer, primer, bootstrap, venv, install, python, required, version, isolated, repo, clone, environment, config
```

# [![logo](/_static/protoprimer.logo.16x16.png)][protoprimer_github] [`protoprimer`][protoprimer_github]

Do you distribute software via repo clone?

Do **not** write manuals to make it runnable.

Instead:

```sh
./prime
# your repo clone
```

```mermaid
%%{init: {"look": "handDrawn", "theme": "neutral"}}%%
flowchart TB;

    pull_manual["`clone`"];
    subgraph manual_steps["manual:"]
        direction TB;
        try_a["try A"];
        do_b["do B"];
        check_c["check C"];
        select_d["select D"];
        more_steps["..."];
    end
    run_manual["`run`"];

    pull_prime["`clone`"];
    subgraph prime_group["protoprimer:"]
        direction TB;
        prime_step["`prime`"];
    end
    run_prime["`run`"];

    pull_manual --> manual_steps;
    try_a --> do_b --> check_c --> select_d --> more_steps;
    manual_steps --> run_manual;

    pull_prime --> prime_group;
    prime_group --> run_prime;

    style manual_steps fill:none;
    style prime_group fill:none;
```

## Why?

Because there is a surprisingly common problem:
> Turn a fresh repo clone into an isolated environment with a runnable software version.

`protoprimer` is **arg-less** stand-alone **idempotent** bootstrap code that transitions:

*   from **chaos** (the many conditions in which a user may invoke it)
*   into **order** (an env-specific `venv` with the **required** `python` version)

```mermaid
%%{init: {"look": "handDrawn", "theme": "neutral"}}%%
flowchart LR;

    subgraph chaos["[chaos]"]
        use_cases["<div style='text-align:left;white-space:nowrap'>• wrong dependencies<br>• different platforms<br>• multiple clones<br>• outside correct venv<br>• inside wrong venv<br>• random cwd<br>• random env vars<br>• nested executions<br>• cloud containers<br>• personal laptops<br>• public artifacts<br>• private artifacts<br>• authn and authz<br>• ...</div>"];

        subgraph proto["protoprimer"]
            subgraph order["[order]"]
                user["user code"];
            end
        end
    end

    style chaos fill:none;
    style use_cases fill:none,stroke:none;
    style proto fill:none;
    style order fill:none;
    style user fill:none;
```

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

When you need a **universal installer** (`diff`-able code, not binary) in your sources for:

<details>
<summary>[robust initialization]</summary>

*   Bootstrapping a cloned repo (local or cloud) to run stuff from it.
*   Preparing a continuous integration job (after cloning a repo).
*   Spinning up a container from a minimal base image.
*   ...

</details>

When you want to **uninstall** a software version by removing its repo clone.

## What?

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

## How?

User repo hosts [proto_kernel.py][proto_kernel] - the `protoprimer` script that **survives the chaos**.

When it runs, it **iteratively restarts** to prepare the environment:

*   Takes off with a **wild** `python` version (whatever is in the `PATH` env var).

*   Switches in-flight to the **required** `python` version.

*   Satisfies a set of DAG-organized pre-conditions on each restart cycle:

    *   navigate the user repo directory structure to discover config and packages

    *   handle global (repo-wide) and local (environment-specific) config

    *   provide authn and authz for internal artifact repositories

    *   use "editable install" for local packages

    *   ...

*   Lands inside a comfy isolated `venv` with all dependencies **pinned**.

    > The user code **takes over** here.

```mermaid
sequenceDiagram
    actor U as actor
    participant P as protoprimer
    participant C as user code

    U->>P: prime
    Note over P: wild python
    P->>P: obtain required python<br>[restart]
    Note over P: required python
    P->>P: create venv<br>[restart]
    Note over P: venv python
    P->>P: install dependencies<br>[restart]
    P->>C: pass control
    Note over C: custom bootstrap<br>pinned dependencies<br>convenient tools<br>testable logic
```

<div style="text-align: center; margin-top: 8em; margin-bottom: 8em;">

Poke your LLM to see where it fits...

</div>

[protoprimer_github]: https://github.com/uvsmtid/protoprimer
[pypl_index]: https://pypl.github.io/
[proto_kernel]: https://github.com/uvsmtid/protoprimer/blob/main/src/proto_code/proto_kernel.py
