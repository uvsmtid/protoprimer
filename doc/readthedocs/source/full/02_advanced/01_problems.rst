Problems
================================================================================

.. stub_include_start

Ultimate goal
********************************************************************************

``protoprimer`` must help eliminate manuals:

*   no (conditional) steps for an author to write
*   no mistakes for a user to make

First problems
********************************************************************************

To eliminate manuals, ``protoprimer`` has to be both:

*   arg-less
*   one-liner

That brings the first problems:

*   Being **arg-less** requires environment-specific configurations to handle differences.

*   Being a **one-liner**, it must "just run" (without asking to install anything).

Elaborated constraints
********************************************************************************


*   No dependencies.

    Because it starts without a ``venv``, it must depend only on the ``python`` standard library.

*   Hosted by the target repo.

    The ``protoprimer`` core must be a copy available in the repo clone (hosted by that repo).

*   A (text) script, not a binary.

    To evolve and be auditable (security), it must be distributed as source code.

*   Limited size -> limited functionality.

*   Private infrastructure support.

    .. see: FT_17_41_51_83.private_artifact_repo.md

    Bootstrap should allow authn/authz for intranet artifact repositories and other resources.

*   Wild ``python`` version.

    .. See: FT_84_11_73_28.supported_python_versions.md

    The ``protoprimer`` core must be startable even by extinct dinosaur ``python`` versions.

*   Required ``python`` version.

    *   Getting a required dependency version in a ``venv`` is **trivial**.

    *   Getting the required ``python`` version is **not**.

        The required ``python`` version must be installed and swapped in-flight (while running that **one-liner**).

*   Isolation per repo clone.

    *   No system-wide or user-local configuration should require changes.

    *   No conflicts with existing system-wide or user-private tools.

    *   Each repo clone is also isolated (specifically, every two clones are independent).

*   Automatic environment-specific configuration.

    Without user input (**arg-less one-liner**):

    *   not only does **everything** have to be found inside the configuration
    *   one of the multiple configurations must be automatically selected (based on the current environment)

*   No fixed configuration paths.

    Support monorepos with any directory structure.

*   Unrestricted choices.

    *   It must provide choice for underlying tooling.

    *   The underlying tooling must also be usable independently of ``protoprimer``.

    After all, ``protoprimer`` only bootstraps.

.. stub_include_stop
