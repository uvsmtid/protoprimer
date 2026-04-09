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

Because this escalates quickly:

*   You may think *"I can create a `venv` manually"*, **but**:

    *   that `venv` has to be created by **every** user

    *   **everyone** has to `activate` it **every** time

    And how to ensure the **required** `python` version to create the `venv`?

*   You may think *"I can use `uv` to ensure the `python` version"*, **but**:

    *   you and your users have to **install** the `uv` executable first

    *   users will be **exposed** to `uv` args like:

        ```bash
        uv pip install -e path/to/project_1 path/to/project_2
        ```

    And you still need to constrain dependency versions for **reproducibility**.

*   You may think *"I can use `requirements.txt` to control versions"*, **but**:

    *   `requirements.txt` may need to depend on the target environment (dev, prod) x (macOS, Linux)

    *   that does not select the `python` version

    And you may still want to extend the bootstrap sequence to configure additional tools.

Eventually, manual mistakes turn that into **partially complete unreproducible mess**.

And **newly pushed updates** may amplify it for everyone (facepalm).

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
