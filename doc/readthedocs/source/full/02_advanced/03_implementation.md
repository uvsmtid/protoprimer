# Implementation

% stub_include_start

To bootstrap, `protoprimer` **restarts**, iteratively preparing the environment:

*   Takes off with a **wild** `python` version (whatever is in the `PATH` env var).

*   Switches in-flight to the **required** `python` version.

*   Satisfies a set of DAG-organized pre-conditions on each restart cycle.

*   Lands inside a comfy isolated `venv` with all dependencies **pinned**.

    > The custom steps take over here.

% stub_include_stop
