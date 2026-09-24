from __future__ import annotations

import enum


class KeyWord(enum.Enum):
    """
    Reused words for semantic linking via these definitions.
    """

    key_input = "input"
    key_primer = "primer"
    key_client = "client"
    key_global = "global"
    key_env = "env"
    key_local = "local"
    key_derived = "derived"

    key_help = "help"

    key_var = "var"
    key_tmp = "tmp"
    key_log = "log"
    key_run = "run"
    key_gen = "gen"
    key_venv = "venv"
    key_cache = "cache"
    key_shell = "shell"
    key_command = "command"

    key_do = "do"
    key_start = "start"
    key_install = "install"
    key_restart = "restart"
    key_print = "print"
    key_prepare = "prepare"

    key_id = "id"
    key_state = "state"
    key_args = "args"
    key_stderr = "stderr"
    key_handler = "handler"
    key_data = "data"
    key_package = "package"
    key_constraints = "constraints"
    key_main = "main"
    key_entry = "entry"
    key_func = "func"
    key_level = "level"
    key_basename = "basename"
    key_script = "script"
    key_path = "path"

    key_mocked = "mocked"
    key_default = "default"
    key_conf = "conf"
    key_effective = "effective"

    key_trace = "trace"
    key_execution = "execution"

    key_configured = "configured"
    key_parsed = "parsed"
    key_executed = "executed"
    key_reached = "reached"
    key_printed = "printed"
    key_triggered = "triggered"
    key_installed = "installed"
    key_updated = "updated"
    key_generated = "generated"
    key_prepared = "prepared"
