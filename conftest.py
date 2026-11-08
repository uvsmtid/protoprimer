import os

from local_test.tmp_dir_helper import get_tmp_dir_abs_path

# Do not collect `git worktree`-s of baseline commits (see `local_contract_compatibility`):
collect_ignore = [get_tmp_dir_abs_path(os.path.dirname(os.path.abspath(__file__)))]
