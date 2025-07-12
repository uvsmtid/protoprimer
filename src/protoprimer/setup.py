import os

import re

# The "distribution root" refers to the top-level directory where the code resides.
# It is the root directory that contains the `setup.py` file itself.
# When installed, `setup.py` will run from the extracted archive:
distrib_root = os.path.dirname(os.path.abspath(__file__))

# Implements this (using the single script directly without a separate `_version.py` file):
# https://stackoverflow.com/a/7071358/441652
version_file = f"{distrib_root}/main/protoprimer/primer_kernel.py"
version_content = open(version_file, "rt").read()
version_regex = r"^__version__ = ['\"]([^'\"]*)['\"]"
regex_match = re.search(version_regex, version_content, re.M)
if regex_match:
    version_string = regex_match.group(1)
else:
    raise RuntimeError(f"Unable to find version string: ${version_file}")

import setuptools

extra_dependencies = []

# To install these extra dependencies use these commands, for example:
# pip install --editable "${client_dir}/"[extra]
extras_require = {
    "extra": extra_dependencies,
}


setuptools.setup(
    name="protoprimer",
    version=version_string,
    author="uvsmtid",
    author_email="uvsmtid@gmail.com",
    description=(
        "self-contained, "
        "stand-alone, "
        "no-deps, "
        "no-args-friendly, "
        "auto-cloning #proto, "
        "environment-driven, "
        "pure-python, "
        "multi-stage extensible DAG bootstrapper #primer "
        "to escape from shell scripting maintenance hell"
    ),
    keywords=(
        "venv virtual environment"
        "env environment"
        "dev development"
        "boot bootstrap bootstrapper"
        "init initialize initializer"
        "check checker"
    ),
    long_description="""
See: https://github.com/uvsmtid/protoprimer
    """,
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Information Technology",
        "Topic :: Terminals",
        "Topic :: System :: Shells",
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
    ],
    # See the sample layout:
    # https://docs.python.org/3.8/distutils/setupscript.html#installing-package-data
    # List all packages/sub-packages (so that they are taken by `package_dir` below):
    packages=setuptools.find_packages(
        where=f"{distrib_root}/main/",
    ),
    # See:
    # https://docs.python.org/3.8/distutils/setupscript.html#listing-whole-packages
    #     The keys to this dictionary are package names,
    #     and an empty package name stands for the root package.
    #     The values are directory names relative to your distribution root.
    #     See "distribution root" above - during installation, `setup.py` will run from the extracted archive.
    package_dir={
        "protoprimer": "./main/protoprimer/",
    },
    # See:
    # https://docs.python.org/3.8/distutils/setupscript.html#installing-package-data
    #     The paths are interpreted as relative to the directory containing the package
    #     (information from the `package_dir` mapping is used if appropriate);
    #     that is, the files are expected to be part of the package in the source directories.
    package_data={
        "protoprimer": [],
    },
    include_package_data=False,
    # FT_84_11_73_28: supported python versions:
    python_requires=">=3.8",
    install_requires=[],
    extras_require=extras_require,
)
