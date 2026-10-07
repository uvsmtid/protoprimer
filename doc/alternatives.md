```{eval-rst}
.. meta::
   :description: How `protoprimer` compares to `uv`, `pyenv`, `mise`, `direnv`, `pdm`, `hatch`, ...
   :keywords: protoprimer, alternatives, comparison, uv, pyenv, mise, direnv, pdm, hatch, ...
```

# Alternatives

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

But all of them have to be **pre-installed**.

The question is:
> Who bootstraps the bootstrappers?

## "True" alternative: manuals

<details>
<summary>For simple cases and for people tolerating details, a sample manual may work:</summary>

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

For software distributed via repo clone,
`protoprimer` collapses the **stack** into one committed script that
requires nothing but a **wild** `python` executable in `PATH`
to bootstrap the **required** `python` per repo clone,
along with **all** the tools for custom steps to complete the process.
