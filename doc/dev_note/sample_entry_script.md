
Script `./cmd/start_app` delegates execution to
function `custom_main` inside
module `local_doc.cmd_start_app` implemented
in `./src/local_doc/main/local_doc/cmd_start_app.py` file.

Normally,
`./cmd/start_app` (inside `./cmd` dir but without `cmd_` prefix in extension-less file)
is implemented by
`cmd_start_app.py` (inside one of the projects, with `cmd_` prefix in `*.py` file).
