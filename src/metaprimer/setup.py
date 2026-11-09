import setuptools

# FT_81_79_98_73.EOL_support.md: an instance of old/new mutually-exclusive dependency formats.
if int(setuptools.__version__.split(".")[0]) >= 77:
    license_kwargs = {"license_expression": "MIT"}
else:
    license_kwargs = {"license": "MIT"}

setuptools.setup(**license_kwargs)
