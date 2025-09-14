
This file can be loaded into LLM agent for initial context.

## Behavior

*   Do not commit changes - human will do this after review.
*   Follow the code style defined below.

## Project overview

The entire project focuses around the single file [primer_kernel.py][primer_kernel.py].
It is supposed to work via its own copy as a stand-alone script in any client repo.
The `protoprimer` repo self-adopts an example of such copy [proto_kernel.py][proto_kernel.py].
There is no need to modify the copy - it is eventually automatically updated.
The copy is also used as an initial library (before `venv` is fully configured) for scripts in [cmd][cmd] directory.

## Bootstrap process

Bootstrap process is implemented as a set of states (listed in `EnvState` enum)
which depend on each other (via list of `parent_states`) forming a DAG.

Each `EnvState` enum item points to the implementation of the state (derived from `StateNode`).

When bootstrap process starts, eventually, method `_eval_state_once` does the job.

The final goal of the bootstrap process is `TargetState.target_full_proto_bootstrap`.

## Code style

*   Try to split any list items on a separate line as much as possible.

*   Use terminating comma `,` for the last item in the list.

*   Try to name every variable with at least 2 words embedded into it.

    For example:

    ```python
    word1_word2: int = 0
    ```

    This simplifies refactoring and search.

*   Do not use trailing comments.

    Instead of this:

    ```python
    some_variable: int = 0 # some comment
    ```

    Use this:

    ```python
    # some comment:
    some_variable: int = 0
    ```

*   When writing tests, use markets `# given:`, `# when:`, `# then:`.

    Put comments (if any) after `# given:`, `# when:`, `# then:` on a separate (next) line.

## Dir structure

Each subdirectory of [src][src] directory contains related subprojects (with corresponding `pyproject.toml`):
*   [protoprimer][protoprimer] is the main project which runs code before `venv` is fully configured
*   [neoprimer][neoprimer] contains extensions with code useful run after `venv` is fully configured
*   [local_repo][local_repo] hosts various non-release-able support scripts for this repo
*   [local_test][local_test] provides non-release-able test help code

---

[primer_kernel.py]: ../../src/protoprimer/main/protoprimer/primer_kernel.py
[proto_kernel.py]: ../../cmd/proto_kernel.py

[local_repo]: ../../src/local_repo
[local_test]: ../../src/local_test
[protoprimer]: ../../src/protoprimer
[neoprimer]: ../../src/neoprimer

[src]: ../../src
[cmd]: ../../cmd
