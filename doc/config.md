```{eval-rst}
.. meta::
   :description: How `protoprimer` configures a repo clone: global vs. local config, JSON format, and effective config
   :keywords: protoprimer, config, configuration, global config, local config, effective config, json
```

# Config

```{contents}
:local:
:depth: 2
```

## Global vs. local config

`protoprimer` distinguishes between:

*   **global** config - repo-wide, committed alongside the code

*   **local** config - environment-specific, not committed

The **local** config overrides the **global** config on a per-clone basis.

## Format

Config files use **JSON**:

*   no external dependencies (no YAML or TOML)
*   no executable code (no `*.py`)

## Effective config

To see the fully resolved configuration - both the values **loaded** from files and the values **derived** from them - run:

```sh
./prime eval
```

This prints the **effective** config: every field shown with its evaluated value, including derived ones.
