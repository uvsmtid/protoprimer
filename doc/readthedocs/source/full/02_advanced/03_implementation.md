# Implementation

% stub_include_start

To bootstrap, `protoprimer` **restarts** iteratively preparing the environment:

*   takes off with a **wild** `python` version (whatever is in the `PATH` env var)
*   switches in-flight to the **required** `python` version
*   reaches a set of (DAG) states on each restart cycle
*   lands inside a comfy isolated `venv` with all dependencies **pinned**

Who wants to re-implement that for every project?

% stub_include_stop
