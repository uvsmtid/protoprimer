
## IDEA config

<details>

<summary>Requirement:</summary>

<br>

Ultimately, all you want is:
*   click-able navigation through sources with usage search
*   click-to-run tests and debugging

</details>

<details>

<summary>Problem:</summary>

<br>

Directory `./.idea/` is not shared because:

*   It keeps automatically mis-marking "prod source root" and "test source root" directories.

*   SDK config is **private** to user, but it is referenced by the **shared** config.

    You cannot keep private and shared configs reliably consistent for all users.

    Besides, the private user config path is annoyingly ugly (and unstable - it depends on the `version`):

    ```
    ~/.config/JetBrains/IntelliJIdea${version}/options/jdk.table.xml
    ```

*   It is problematic to pin IDEA for specific config layout.

    It may split modules per `*.iml` files or combine them at will.

The automation by IDEA feels wrong and messy.

</details>

<details>

<summary>Solution:</summary>

<br>

Configure (fight) IDEA manually:
*   use `./venv/bin/python` as the interpreter

*   mark as "prod source roots" directories like `./src/*/main/`

*   mark as "test source roots" directories like `./src/*/test/`

*   mark to exclude:

    *   `./venv/`
    *   `./log/`
    *   `./tmp/`
    *   ...

</details>
