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

To remain an **arg-less** one-liner, `protoprimer` takes customization input from its config.

## Format

<!--
FT_48_62_07_98.config_format.md
-->

JSON is used as the [config_format][FT_48_62_07_98.config_format.md]:

*   primarily to avoid external dependencies (as with YAML or TOML)
*   secondarily to avoid executable code (as with `*.py`)

## Config: global vs local

<!--
FT_23_37_64_44.global_vs_local.md
FT_92_51_35_07.local_env_link.md
-->

`protoprimer` distinguishes between:

*   **global** config: repo-wide

*   **local** config: environment-specific

The **local** config overrides the **global** config on a per-clone basis.

The currently selected environment is indicated by [local_env_link][FT_92_51_35_07.local_env_link.md].

## Config leaps

<!--
FT_59_95_81_63.tree_shape.md
FT_89_41_35_82.conf_leap.md
-->

`protoprimer` supports **any** directory [tree_shape][FT_59_95_81_63.tree_shape.md] for user repos.

To find config files, it goes through the ordered [conf_leap][FT_89_41_35_82.conf_leap.md]-s:

```{include} feature_topic/FT_89_41_35_82.conf_leap.md
:start-after: <!-- diagram:conf_leap:start -->
:end-before: <!-- diagram:conf_leap:end -->
```

Each config leap tells where to find the next one.

Going through all of them loads all the config info.

```
^/                                      # repo_root = ref_root
│
├─ src/
│  └─ proto_code/                       # <- `./src/proto_code`
│     ├─ proto_kernel.py                # copy of `protoprimer.primer_kernel`
│     ├─ proto_kernel.json              # `leap_primer`
│     └─ ...
│
├─ gconf/                               # <- `./gconf` (global config)
│  ├─ proto_kernel.json                 # `leap_client`
│  └─ ...
│
├─ lconf/                               # <- `./lconf` (local config)
│  │                                    # symlink to (e.g.) `./dst/default_env/`
│  ├─ proto_kernel.json                 # `leap_env`
│  └─ ...
│
├─ dst/                                 # dst ~ destination environments
│  ├─ default_env/
│  │  ├─ proto_kernel.json              # the same file as `./lconf/proto_kernel.json`
│  │  └─ ...
│  └─ ...
│
└─ ...
```

## Derived config

<!--
FT_00_22_19_59.derived_config.md
-->

The [derived_config][FT_00_22_19_59.derived_config.md] contains extra fields.

These field values are computed from runtime data, **local** or **global** configs.

Any logic can be used to evaluate them.

## Effective config

<!--
FT_19_44_42_19.effective_config.md
-->

To see the fully resolved configuration, run:

```sh
./prime eval
```

This prints the **effective** config - every field shown with its evaluated value.

[FT_00_22_19_59.derived_config.md]: feature_topic/FT_00_22_19_59.derived_config.md
[FT_48_62_07_98.config_format.md]: feature_topic/FT_48_62_07_98.config_format.md
[FT_89_41_35_82.conf_leap.md]: feature_topic/FT_89_41_35_82.conf_leap.md
[FT_92_51_35_07.local_env_link.md]: feature_topic/FT_92_51_35_07.local_env_link.md
[FT_59_95_81_63.tree_shape.md]: feature_topic/FT_59_95_81_63.tree_shape.md
