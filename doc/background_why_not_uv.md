```{eval-rst}
.. meta::
   :description: Why `protoprimer` wraps `uv` instead of replacing it
   :keywords: background, uv, wrapper, bootstrap
```

# Why not `uv`?

Make no mistake: `protoprimer` (optionally) relies on `uv`.

The `python` script bootstraps `uv`, then runs `uv`.

## Problem: need a wrapper

`uv` is hardly **arg-less** and **single-step** without a wrapper script:

*   Its binary has to be prepared.
*   Its args have to be provided.
*   Project-specific steps require more than `uv`.

## Solution: have a wrapper

Feel the difference:

| `protoprimer` | `uv`                                  |
|---------------|---------------------------------------|
| `./bootstrap` | `uv run python -m module_a.bootstrap` |
| `./app_1`     | `uv run python -m module_b.app_1`     |
| `./app_2`     | `uv run python -m module_c.app_2`     |

Relying on `python` first:
*   is more robust for the **single-touch** bootstrap (`python` is more ubiquitous than `uv`)
*   uses **easily modifiable** `python` text code to wrap calls to any binary (like `uv`)
