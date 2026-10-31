```{eval-rst}
.. meta::
   :description: Step-by-step tutorial of `protoprimer` bootstrapping a `python` repo from scratch
   :keywords: tutorial, walkthrough, bootstrap, venv, python, repo
```

# Tutorial

```{toctree}
:hidden:
:maxdepth: 1
:titlesonly:

Init flat repo <tutorial_init_flat_repo>
Boot env <tutorial_boot_env>
Form nested repo <tutorial_form_nested_repo>
Start app <tutorial_start_app>
Clean repo root <tutorial_clean_repo_root>
Enable updates <tutorial_enable_updates>
```

The tutorial walks through the main use cases of `protoprimer`.

A `git` repo is developed from scratch to gradually introduce concepts and features.

The pages build on each other and steps have to be executed in order:

| Page                                             | Outcome                                                           |
|--------------------------------------------------|-------------------------------------------------------------------|
| [Init flat repo](tutorial_init_flat_repo.md)     | a basic flat `python` repo with a project descriptor              |
| [Boot env](tutorial_boot_env.md)                 | a working env bootstrapper via `./proto_kernel.py` in a flat repo |
| [Form nested repo](tutorial_form_nested_repo.md) | a realistic nested `python` repo with `src/` and updated config   |
| [Start app](tutorial_start_app.md)               | a working app starter via `./proto_kernel.py` in a nested repo    |
| [Clean repo root](tutorial_clean_repo_root.md)   | a dedicated `proto_code` dir with a dedicated `./prime` script    |
| [Enable updates](tutorial_enable_updates.md)     | an update-able `proto_kernel.py` via a `protoprimer` dependency   |

---

Next: [Init flat repo](tutorial_init_flat_repo.md)
