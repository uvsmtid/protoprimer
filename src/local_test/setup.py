import os

import setuptools

setuptools.setup(
    name="local_test",
    classifiers=[
        # This package is local ana is never published:
        "Private :: Do Not Upload",
    ],
    packages=setuptools.find_packages(
        where=f"./main/",
    ),
    package_dir={
        "local_test": "./main/local_test/",
    },
    package_data={
        "local_test": [],
    },
    include_package_data=False,
    # FT_84_11_73_28: supported python versions:
    python_requires=">=3.8",
    install_requires=[
        "pyfakefs",
        "coverage",
    ],
)
