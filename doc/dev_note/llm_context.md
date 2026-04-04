
This file can be loaded into an AI/LLM agent for the initial context.

## Expected AI/LLM behavior

*   Leave changes uncommitted - they will be committed by a human after review.
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

The final goal of the bootstrap process is `TargetState.target_proto_bootstrap_completed`.

## Testing changes

*   All you need to do is to run `pytest` to see the errors and fix them under `./src/` dir only.
*   Any imports inside `./src/` files should not escape that `./src/` directory.
*   Do not change `sys.path` or `PYTHONPATH` - these are not acceptable fixes.
*   Do not install anything with `pip`.
*   Run tests only under the [test_fast_slim_max_mocked][test_fast_slim_max_mocked] directory to get quick feedback.

Only when your changes are under `test_slow_integrated` directory,
run `pytest` for all directories.

---

[primer_kernel.py]: ../../src/protoprimer/main/protoprimer/primer_kernel.py
[proto_kernel.py]: ../../cmd/proto_code/proto_kernel.py

[local_repo]: ../../src/local_repo
[local_test]: ../../src/local_test
[protoprimer]: ../../src/protoprimer
[neoprimer]: ../../src/neoprimer

[src]: ../../src
[cmd]: ../../cmd

[test_fast_slim_max_mocked]: ../../src/protoprimer/test/test_protoprimer/test_fast_slim_max_mocked
[test_slow_integrated]: ../../src/protoprimer/test/test_protoprimer/test_slow_integrated
