---
seo_title: "protoprimer vs: uv, pyenv, mise, direnv - comparison"
---

```{eval-rst}
.. meta::
   :description: How protoprimer compares to uv, pyenv, mise, direnv, pdm, and hatch for bootstrapping an isolated Python environment in a repo clone.
   :keywords: protoprimer, alternative, comparison, uv, pyenv, mise, direnv, pdm, hatch
```

# Alternative

```{contents}
:local:
:depth: 2
```

## What is `protoprimer` **NOT** an alternative to?

`protoprimer` can work together with all these tools:

*   `python` providers:

    *   `uv`

    *   `pyenv`

    *   ...

*   dev-env managers:

    *   `mise`

    *   `direnv`

    *   ...

*   project managers:

    *   `uv`

    *   `pdm`

    *   `hatch`

    *   ...

*   build systems:

    *   `make`

    *   ...

**But** all of the above have to be **pre-installed**!

The question is:
> Who bootstraps the bootstrappers?

## "True" alternative: manual

<details>
<summary>For simple cases, a sample manual may work:</summary>

*   **Download** specific `python` version.

*   **Configure** to use that `python` version.

*   **Configure** private artifact repositories (if any).

*   **Create** `venv`:

    ```shell
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

*   **Ensure** the correct `venv` is activated to run:

    ```shell
    ./some_app
    ```

</details>

Have we missed any details?

What can possibly go wrong when doing it manually?

## Falling forward to `protoprimer`

Automating away manuals helps.

Using `shell` is an obvious but limiting option:
> [Why not `shell`?][doc_background_why_not_shell]

Instead, `protoprimer` collapses the **stack** into one committed script that
requires nothing but a **wild** `python` executable in `PATH`
to bootstrap the **required** `python` per repo clone,
along with **all** the version-pinned tools
for custom steps to complete the process reliably.

[doc_background_why_not_shell]: background_why_not_shell.md
