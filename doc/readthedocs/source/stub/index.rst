.. meta::
   :description: ``protoprimer`` is an arg-less ``python`` one-liner to bootstrap a ``venv`` for repo clones
   :keywords: bootstrap, venv, install, python, required, version

protoprimer
====================================================================

.. include:: /full/01_basic/01_intro.rst
    :start-after: stub_include_start
    :end-before: stub_include_stop

Why?
--------------------------------------------------------------------------------

Because this never ends:

*   You may think *"I can create a* ``venv`` *manually"*, **but**:

    *   that ``venv`` has to be created by **every** user

    *   **everyone** has to ``activate`` it **every** time

    And how to ensure the **required** ``python`` version to create the ``venv``?

*   You may think *"I can use* ``uv`` *to ensure the* ``python`` *version"*, **but**:

    *   you and your users have to **obtain** the ``uv`` executable

    *   users will be **exposed** to ``uv`` args like:

        .. code-block:: bash

            uv pip install -e path/to/package_1 path/to/package_2

    And you still need to constrain dependency versions for **reproducibility**.

*   You may think *"I can use* ``requirements.txt`` *to control versions"*, **but**:

    *   ``requirements.txt`` may need to depend on the target environment (dev, prod) x (macOS, Linux)

    *   that does not select the ``python`` version

    And you may still want to extend bootstrap to other tools, SDK-s, customizations, ...

How?
--------------------------------------------------------------------------------

.. include:: /full/02_advanced/03_implementation.rst
    :start-after: stub_include_start
    :end-before: stub_include_stop

Quick dive
--------------------------------------------------------------------------------

.. include:: /full/02_advanced/01_solutions.rst
    :start-after: stub_include_start
    :end-before: stub_include_stop
