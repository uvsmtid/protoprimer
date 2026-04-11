# Intro

% stub_include_start

Want a **one-liner** to bootstrap isolated envs for every repo clone?

```bash
./prime
```

This invokes `protoprimer` - an **arg-less** stand-alone script that switches:

*   from **chaos**: regardless of conditions it was invoked in by a user
*   into **order**: reproduces populated `venv` with the **required** `python` version

<br/>

<details>
<summary>
Then, <code>protoprimer</code> transfers control to custom steps for <strong>anything</strong> else:
</summary>

*   verify env vars
*   install `git` hooks
*   configure other SDK-s
*   ... [you name it]

</details>

% stub_include_stop
