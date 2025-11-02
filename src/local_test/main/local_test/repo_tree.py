import os
from contextlib import contextmanager

import protoprimer


@contextmanager
def change_to_known_repo_path(path_from_repo_root="."):
    """
    This function changes the current dir to a known path within the repo root.

    This allows any other code accessing files by relative paths to rely on the stable path within the repo.
    """

    start_dir_abs_path = os.path.dirname(protoprimer.__file__)
    curr_dir_abs_path = start_dir_abs_path
    os.chdir(curr_dir_abs_path)

    try:
        signature_dir_path = os.path.join(".github", "workflows")
        # This will work for anything running with the current dir under repo root dir.
        # We know that path `signature_dir_path` (can be anything) is a dir relative to repo root dir.
        # Walk up from `start_dir_abs_path` until we see `signature_dir_path` - if we see it, we are in repo root dir.

        while not os.path.isdir(os.path.join(os.getcwd(), signature_dir_path)):
            os.chdir(os.path.dirname(curr_dir_abs_path))
            curr_dir_abs_path = os.path.abspath(os.getcwd())
            # Fail when walking up does not change dir (we are in the system root):
            if curr_dir_abs_path == os.path.dirname(curr_dir_abs_path):
                raise RuntimeError(
                    f"cannot reach repo root walking up from the given start path: {start_dir_abs_path}"
                )

        # Desired path:
        os.chdir(path_from_repo_root)
        yield
    finally:
        os.chdir(start_dir_abs_path)
