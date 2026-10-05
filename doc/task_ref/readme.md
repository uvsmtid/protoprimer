NOTE: AI-generated

## Purpose

Every `TODO` in [primer_kernel.py][primer_kernel.py] is associated with a doc file.

All `TODO`-s are grouped by similarity (by meaning).
Each group gets its own `TODO_*.md` file.
In addition to the in-place text,
the file gives a wider explanation with links to associated docs and other `TODO_*.md` files.

There are no "unrelated" `TODO`-s:
a `TODO` which does not fit any group is a group of one and gets its own `TODO_*.md` file.

## Conventions

*   Create a new `TODO_*.md` file for one group at a time:

    Generate its tag only after the file for the previous tag is created:

    ```shell
    ./cmd/gen_next_doc_id doc/task_ref
    ```

*   Associate the in-place `TODO`-s with the file (only after the file exists):

    Keep the original `TODO` text as is and add a comment line above it (with the same indentation):

    ```python
    # TODO: TODO_NN_NN_NN_NN.some_semantic_name.md:
    # TODO: <original text stays here>
    ```

*   A `TODO` already associated with another doc (e.g. `FT_*` or `UC_*` - not under `doc/task_ref/`) needs no additional `TODO_*.md` file.

*   A `TODO` directly under an already tagged `TODO` (the same block) is not tagged again.

*   Inside a docstring, the tag line has the same form but without the leading `#`:

    ```python
    """
    TODO: TODO_NN_NN_NN_NN.some_semantic_name.md:
    TODO: <original text stays here>
    """
    ```

*   Before creating a new `TODO_*.md` file, check the existing ones (to avoid duplicating the same issue):

    Group `TODO`-s by what they try to do (by meaning), not by the wording of the comment.

[primer_kernel.py]: ../../src/protoprimer/main/protoprimer/primer_kernel.py
