```{eval-rst}
.. meta::
   :description: Dictionary of `protoprimer` terms: `proto_code`, `proto_kernel`, `entry_script`, `boot_env`, `start_app` and others
   :keywords: dictionary, terms, glossary, protoprimer
```

# Dictionary

```{contents}
:local:
:depth: 2
```

This doc defines the terms used in the [`protoprimer`][protoprimer_link] project.

---

<a id="boot_env"></a>

## `boot_env`

The entry function that bootstraps an environment.

See details in [boot_env][FT_85_17_35_21.boot_env.md].

See also:
*   [entry_func](#entry_func)
*   [start_app](#start_app)

---

<a id="client_code"></a>

## `client_code`

The software project that relies on `protoprimer`.

---

<a id="derived_config"></a>

## `derived_config`

The config part that contains the fields with values derived from field values in config files.

See details in [derived_config][FT_00_22_19_59.derived_config.md].

See also:
*   [effective_config](#effective_config)

---

<a id="effective_config"></a>

## `effective_config`

The `protoprimer` config with all fields shown at their evaluated values.

See details in [effective_config][FT_19_44_42_19.effective_config.md].

See also:
*   [derived_config](#derived_config)

---

<a id="entry_func"></a>

## `entry_func`

The `proto_kernel` function that a client script calls to start the work: either `boot_env` or `start_app`.

See details in [entry_func][FT_25_62_13_55.entry_func.md].

See also:
*   [boot_env](#boot_env)
*   [start_app](#start_app)

---

<a id="entry_script"></a>

## `entry_script`

The text script that a user runs from a shell, for example:

```sh
./cmd/start_app_example
```

It only delegates the real work to `proto_kernel`.

See details in [entry_script][FT_75_87_82_46.entry_script.md].

---

<a id="main_func"></a>

## `main_func`

This is just a pattern in `python` to factor the `__main__` part out into a `main` function -
see [more info][google_python_main_function].

---

<a id="proto_code"></a>

## `proto_code`

Any code designed to be executed by an arbitrary `python` version, outside `venv`.

See details in [proto_code][FT_90_65_67_62.proto_code.md].

---

<a id="proto_kernel"></a>

## `proto_kernel`

`proto_kernel` is a **copy** of `protoprimer.primer_kernel` module stored **together** with the client code.

It is normally named as `proto_kernel.py` to disambiguate from `protoprimer.primer_kernel`.

See details in [proto_kernel][FT_87_17_49_36.proto_kernel.md].

---

<a id="ref_root"></a>

## `ref_root`

The directory inside a user repo that serves as the base for most relative paths.

Do not confuse with `repo_root`.

See details in [ref_root][FT_51_86_20_81.ref_root.md].

See also:
*   [repo_root](#repo_root)
*   [script_dir](#script_dir)

---

<a id="repo_root"></a>

## `repo_root`

The root directory of the repository with the user code.

Do not confuse with `ref_root`.

See also:
*   [ref_root](#ref_root)

---

<a id="script_dir"></a>

## `script_dir`

The absolute path to the currently running script (without its `basename`).

See details in [script_dir][FT_18_38_32_22.script_dir.md].

---

<a id="start_app"></a>

## `start_app`

The entry function that starts an application in a bootstrapped environment.

See details in [start_app][FT_05_08_64_67.start_app.md].

See also:
*   [boot_env](#boot_env)
*   [entry_func](#entry_func)

[protoprimer_link]: https://github.com/uvsmtid/protoprimer
[google_python_main_function]: https://google.com/search?q=python+main+function
[FT_00_22_19_59.derived_config.md]: feature_topic/FT_00_22_19_59.derived_config.md
[FT_19_44_42_19.effective_config.md]: feature_topic/FT_19_44_42_19.effective_config.md
[FT_25_62_13_55.entry_func.md]: feature_topic/FT_25_62_13_55.entry_func.md
[FT_51_86_20_81.ref_root.md]: feature_topic/FT_51_86_20_81.ref_root.md
[FT_05_08_64_67.start_app.md]: feature_topic/FT_05_08_64_67.start_app.md
[FT_18_38_32_22.script_dir.md]: feature_topic/FT_18_38_32_22.script_dir.md
[FT_75_87_82_46.entry_script.md]: feature_topic/FT_75_87_82_46.entry_script.md
[FT_85_17_35_21.boot_env.md]: feature_topic/FT_85_17_35_21.boot_env.md
[FT_87_17_49_36.proto_kernel.md]: feature_topic/FT_87_17_49_36.proto_kernel.md
[FT_90_65_67_62.proto_code.md]: feature_topic/FT_90_65_67_62.proto_code.md
