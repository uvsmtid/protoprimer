
This file can be loaded into an AI/LLM agent for the initial context.

## Expected AI/LLM behavior

*   Do not commit or stage changes. Leave them. They will be committed by a human after review.
*   When changes have been made, use the testing method described (below).
*   Follow the code style (below).
*   To not fix TODO-s. Focus on the specific task instead. A human will clean those TODO-s without you.

## Project overview

The entire project focuses around the single file [primer_kernel.py][primer_kernel.py].
It is supposed to work via its own copy as a stand-alone script in any client repo.

## Bootstrap process

Bootstrap process is implemented as a set of states (listed in `EnvState` enum)
which depend on each other (via list of `parent_states`) forming a DAG.

Each `EnvState` enum item points to the implementation of the state (derived from `StateNode`).

When a bootstrap process starts, eventually, method `_eval_state_once` does the job.

The final goal of the bootstrap process is `TargetState.target_full_proto_bootstrap`.

## Testing changes

*   All you need to do is to run `pytest` to see the errors and fix them under `./src/` dir only.
*   Any imports inside `./src/` files should not escape that `./src/` directory.
*   Do not change `sys.path` or `PYTHONPATH` - these are not acceptable fixes.
*   Do not install anything with `pip`.
*   Run tests only under the [test_fast_mocked][test_fast_mocked] directory to get quick feedback.

Only when your changes are under `test_slow_integrated` directory,
run `pytest` for all directories.

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

*   When writing tests, use markers: given, when, then.

    Put comments (if any) after on a separate (next) line after the marker.
    Separate each marker by an empty line before and after.

    ```

    # given:

    # when:

    # then:

    ```

*   Instead of direct strings, try to use constants.

    It is easier to refactor and inspect relationships in the code.

    There are many existing constants and enums defined in [primer_kernel.py][primer_kernel.py].

    For test-case-specific strings, define those constants for that test only.

---

[primer_kernel.py]: ../../src/protoprimer/main/protoprimer/primer_kernel.py
[proto_kernel.py]: ../../cmd/proto_code/proto_kernel.py

[local_repo]: ../../src/local_repo
[local_test]: ../../src/local_test
[protoprimer]: ../../src/protoprimer
[neoprimer]: ../../src/neoprimer

[src]: ../../src
[cmd]: ../../cmd

[test_fast_mocked]: ../../src/protoprimer/test/test_protoprimer/test_fast_mocked
[test_slow_integrated]: ../../src/protoprimer/test/test_protoprimer/test_slow_integrated
