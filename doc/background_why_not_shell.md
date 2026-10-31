```{eval-rst}
.. meta::
   :description: Why `protoprimer` avoids `shell` scripts and bootstraps `python` with `python`
   :keywords: background, shell, python, bootstrap, testing
```

# Why not `shell`?

Main reason:
> Your org **does not test** `shell` scripts.

<details>
<summary>Let's expand:</summary>

The `shell` paradox:

> We start with `shell` because it is "simple" to start.
>
> But `shell` is also all of these:

*   ❌ (unit) test code for `shell` scripts is next to none
*   ❌ no default error detection - forget `set -e` and "everything is fine"
*   ❌ cryptic "write-only" syntax - `echo "${file_path##*/}"` vs `os.path.basename(file_path)`
*   ❌ subtle, error-prone pitfalls, `shopt` nuances
*   ❌ unpredictable local/user overrides - `PATH` pointing to unexpected binaries
*   ❌ deceptively cross-platform even on *nixes - divergent behaviors: macOS vs Linux
*   ❌ no stack traces on failure - instead, noisy and excessive logging
*   ❌ limited native data structures, no nested ones
*   ❌ no modularity - code larger than one-page-one-file is cumbersome
*   ❌ no external libraries/packages, no enforceable dependencies
*   ❌ interdependency via `source`-ing - an entangled mess
*   ❌ being so unpredictable makes `shell` scripts a high security risk
*   ❌ slow
*   ...

</details>

In short, `shell` is a very poor language choice for evolving software.

<details>
<summary>What if we automated with <code>python</code> instead?</summary>

*   **Ubiquity**: shares the same "pre-installed-anywhere" scripting niche (as `shell`).
*   **Mindshare**: leverages the vast ecosystem everyone is exposed to (as `shell`).
*   **Sanity**: testable, structured code with a clear syntax (**not** as `shell`).

</details>

## Problem: who bootstraps the bootstrapper?

Every time some `repo.git` is cloned, it has to be prepared before it can be useful.

Because `python` is **not** ready, `shell` is used (again!) to make it ready.

<div style="text-align:center;">
    <iframe
        width="360" height="640"
        src="https://www.youtube.com/embed/gNYgeAxCK3M?loop=1&playlist=gNYgeAxCK3M"
        title="youtube"
        frameborder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        allowfullscreen
    ></iframe>
</div>

Ultimately, why not use `python` to unwrap itself?

## Solution: immediately runnable `python`

Eliminate dependency on `shell`:

<ul style="list-style: none; padding-left: 0 !important;">
<li>➖ instead of relying on a <code>shell</code> executable to bootstrap <code>python</code></li>
<li>➕ rely on a <code>python</code> executable (any version) to bootstrap <code>python</code> (required version)</li>
</ul>

An app started via `protoprimer` switches to `venv` - no (explicit) `activate` needed:

```sh
./hello_world
```

See the difference:

```{include} ../readme.md
:start-after: <!-- diagram:sh_vs_py:start -->
:end-before: <!-- diagram:sh_vs_py:end -->
```

<details>
<summary>[minimal pre-conditions]</summary>

*   only naked `python` of **unpredictable version** in `PATH`
*   **no** pre-installed dependencies (ignored if any)
*   **no** pre-activated `venv` (ignored if any)
*   **no** special `shell` config
*   **no** user CLI args (by default)
*   ...

</details>

Looks identical, yet `protoprimer` **pins** and **isolates** dependencies, while `shell` does **not**.
