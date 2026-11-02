---
seo_title: "protoprimer background: why primer, single-step bootstrap"
---

```{eval-rst}
.. meta::
   :description: Why protoprimer is a primer committed to your repo: repo clones get instant updates, full sources, and a single reproducible setup step.
   :keywords: background, primer, repo clone, reuse, one-liner, updates
```

# Why primer?

Distributing software via repo clones has its benefits:
*   instant updates in both directions (push or pull)
*   comprehensive LLM support: full sources, fast evolution

Making software reliably runnable in each repo clone requires an isolated environment.

## Problem: avoid extra preparations

Users want a **single reproducible step** to make software runnable - an end-to-end command:

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

For users, this essentially equates the two:
> "installing the reusable primer" == "cloning a repo"

Because the committed primer is text (not binary), auditing is straightforward.

[proto_kernel]: https://github.com/uvsmtid/protoprimer/blob/main/src/proto_code/proto_kernel.py
