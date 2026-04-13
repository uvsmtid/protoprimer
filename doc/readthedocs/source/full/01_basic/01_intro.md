# Intro

% stub_include_start

Want a **one-liner** to bootstrap isolated envs for every repo clone?

```bash
./prime
```

Invoke `protoprimer` - an **arg-less** stand-alone script that switches:

*   from **chaos** (the many conditions in which a user may invoke it)
*   into **order** (an env-specific `venv` with the **required** `python` version)

<br/>

<details>
<summary>
Then, <code>protoprimer</code> transfers control to custom steps for <strong>anything</strong> else:
</summary>

*   verify the env conditions (local, cloud)
*   install `git` hooks
*   configure other SDKs
*   ... [you name it]

</details>

% stub_include_stop
