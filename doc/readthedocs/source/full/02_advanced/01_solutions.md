# Solutions

## Overview

% stub_include_start

### Ultimate goal

<details><summary></summary>

`protoprimer` replaces **manuals** for bootstraps and updates:

*   no (conditional) steps for an author to write
*   no mistakes for a user to make

... **saving human time** for both authors and users **repeatedly**.

</details>

### First challenges

<details><summary></summary>

To eliminate manuals, `protoprimer` has to solve both:

*   Being **arg-less**:

    it requires environment-specific configurations to handle differences.

*   Being a **one-liner**:

    it must "just run" (without asking to install anything).

</details>

### Multiple constraints

<details><summary></summary>

*   Compatible with a wild `python` version.

    % See: FT_84_11_73_28.supported_python_versions.md

    Be able to run even with "extinct dinosaur" `python` versions.

*   No dependencies.

    It starts without a `venv`.

    Therefore, it must depend only on the standard `python` library.

*   A copy hosted by the target repo.

    It has to be available immediately after cloning the repo.

    Therefore, it must be hosted by the repo as a stand-alone copy.

*   A (text) script, not a binary.

    Changes have to be auditable in the repo (for security).

    Therefore, it must be distributed as source code (text).

*   Single file, limited size.

    To keep the approach sane:
    *   it should be a single file, not multiple
    *   the size should be in kilobytes, not megabytes

</details>

### Primary features

<details><summary></summary>

*   Switch to required `python` version.

    *   Getting a required dependency version in a `venv` is **trivial**.

    *   Provisioning the required `python` version is **not**.

        The required `python` version must be installed first.

        Then, it is swapped in-flight (while running that **one-liner**).

*   Support monorepos.

    This requires support for any directory structure.

*   Automatic environment-specific configuration.

    Without user input (arg-less one-liner):

    *   not only must **all settings** come from configuration

    *   but one of the multiple configurations must be auto-selected

*   Support private infrastructure.

    % See: FT_17_41_51_83.private_artifact_repo.md

    It should allow authn/authz to access intranet artifact repositories.

*   Isolate per repo clone.

    *   No system-wide or user-local configuration should require changes.

    *   No conflicts with existing system-wide or user-private tools.

    *   Updating any two repo clones should not affect each other.

*   Support dynamic `import` to avoid shebang length limitation.

    To run scripts in `venv`, shebang can be used.

    The shebang length limit is typically 128 chars.

    Therefore, a `venv` with long paths cannot be accessed via shebang.

    Instead, support dynamic `import` with any path length.

*   Unrestricted options to delegate.

    *   It must be possible to pass control to any tools.

    *   The tools must also be usable independently of `protoprimer`.

    After all, `protoprimer` must only bootstrap - the rest is delegated.

</details>

% stub_include_stop
