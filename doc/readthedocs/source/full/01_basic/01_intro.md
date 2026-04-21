# Intro

% stub_include_start

Want a **one-liner** to bootstrap isolated envs for every repo clone?

```bash
./prime
```

Invoke `protoprimer` - an **arg-less** stand-alone script that switches:

*   from **chaos** (the many conditions in which a user may invoke it)
*   into **order** (an env-specific `venv` with the **required** `python` version)

Eventually, `protoprimer` transfers control to custom steps for **anything** else...
<details>
<summary>
</summary>

*   provision other SDKs

*   verify system/user config (local, cloud)

*   install `git` hooks

*   generate env-specific code

*   ... [you name it]

</details>

% stub_include_stop
