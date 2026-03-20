Problems
================================================================================

.. stub_include_start

Ultimate goal
********************************************************************************

``protoprimer`` must help eliminates manuals:

*   no (conditional) steps for author to write and maintain
*   no mistakes in multiple steps for user to make, no CLI args to select

Fist problems
********************************************************************************

To achieve that ``protoprimer`` has to be both:

*   arg-less
*   one-liner

These two together require solutions for several other problems:

*   Being one-liner requires ubiquitous tool.

    Requiring **wild** ``python`` version is the simplest solution.

    In rare cases, when any ``python`` is not available, it is installed via generic tools and common knowledge.

*   Being arg-less requires support for environment-specific configuration.

    When no user input is expected:

    *   not only everything has to be pulled from the configuration
    *   the configuration must be evaluated depending on the current environment

Additional constraints
********************************************************************************

*   Hosting by the target repo itself.

    The core ``protoprimer`` implementation must be a copy available on repo clone (hosted by that repo).

    To evolve and be auditable, it must be a (text) script, not a binary.

*   Support private infrastructure.

    .. see: FT_17_41_51_83.private_artifact_repo.md

    Bootstrap should allow authn/authz for internal artifact repositories and other resources.

*   No dependencies.

    Because it starts without ``venv``, it must initially depend only on ``python`` standard library.

*   Required ``python`` version.

    *   Getting required dependency version in ``venv`` is **trivial**.

    *   Getting required ``python`` version before ``venv`` is even created is **not**.

        The required ``python`` version must be installed and switched to while running that one-liner.

*   Isolation per git clone.

    *   No user config must be required to change.

    *   No conflicts with existing system-wide or user-local tools must be created.

    *   Each repo clone is also isolated.

*   No fixed configuration paths.

    Support monorepos with any directory structure.

*   Limited size limits functionality.

    The immediate thought would be "delegate", but that is only possible when ``venv`` is populated.

*   Do not restrict choices.

    *   It must provide choice for underlying tooling.

    *   The underlying tooling must also be usable independently of ``protoprimer``.

.. stub_include_stop
