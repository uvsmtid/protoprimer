
There are the following test perimeters (from min to max):

*   [test_fast_slim_max_mocked][test_fast_slim_max_mocked]

    These are the thinnest contour. It tries to mock every call outside the function or class.

*   [test_fast_fat_min_mocked][test_fast_fat_min_mocked]

    This tries to mock all external OS calls (like `os.execv` or file IO).
    The code still executes within the same OS process with the test runner.
    This allows running (almost) end-to-end tests in debug mode.
    The tests are also very fast relatively to [test_slow_integrated][test_slow_integrated].

*   [test_slow_integrated][test_slow_integrated]

    This is the thickest contour. It does not mock anything and calls external commands.
    It is relatively slow (especially, for installation of packages via `pip`),
    but provides the confidence that things are not broken in realistic conditions.

To run tests in PyCharm, there are two configurations:

*   [pytest_fast.run.xml][pytest_fast.run.xml]

    Run everything except [test_slow_integrated][test_slow_integrated].

*   [pytest_all.run.xml][pytest_all.run.xml]

    Run everything.

---

[test_fast_slim_max_mocked]: ../../src/protoprimer/test/test_protoprimer/test_fast_slim_max_mocked
[test_fast_fat_min_mocked]: ../../src/protoprimer/test/test_protoprimer/test_fast_fat_min_mocked
[test_slow_integrated]: ../../src/protoprimer/test/test_protoprimer/test_slow_integrated

[pytest_fast.run.xml]: ../../.run/pytest_fast.run.xml
[pytest_all.run.xml]: ../../.run/pytest_all.run.xml
