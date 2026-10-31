```{eval-rst}
.. meta::
   :description: Why `protoprimer` is a primer committed to the user repo: repo clones get instant updates and full sources
   :keywords: background, primer, repo clone, reuse, one-liner, updates
```

# Why primer?

Distributing software via repo clones has its benefits:
*   instant updates in both directions (push or pull)
*   comprehensive LLM support: full sources, fast evolution

To make software runnable in each repo clone, it requires an isolated environment.

## Problem: avoid extra preparations

Ideally, users want a **single reproducible step** to make software runnable - an end-to-end command:

<details>
<summary>[imagine otherwise]</summary>

Multiple manual steps are **tedious and error-prone**:
*   **users**, and repo **clones** they maintain, **multiply**
*   subsequent update **avalanches** into re-execution of steps
*   the sequence of steps **depends** on the environment state
*   **non-isolated** repo clones conflict in dependency versions
*   partial failures, re-ordering, mistakes, ... turn into **a support nightmare**

</details>

But how do we reuse the end-to-end command without making the user install it first?

## Solution: host a primer copy

The core `protoprimer` functionality is hosted in the user repo:
> [`proto_kernel.py`][proto_kernel] is an auto-update-able copy of `protoprimer.primer_kernel`.

For users, this essentially combines "cloning a repo" with "installing the reusable primer".

Because the committed primer is a text code (not a binary one), the audit is straightforward.

[proto_kernel]: https://github.com/uvsmtid/protoprimer/blob/main/src/proto_code/proto_kernel.py
