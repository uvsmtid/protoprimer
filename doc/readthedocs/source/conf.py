# Configuration file for the Sphinx documentation builder.
import os

# TODO: This is a temporary option to have basic `readthedocs` page while the rest of the docs are in progress.
#       When changed here, it should also be changed in `./index.rst` (automation did not work):
is_full_protoprimer_content = False
if is_full_protoprimer_content:
    tags.add("protoprimer_full")
else:
    tags.add("protoprimer_stub")


def import_proto_kernel(proto_kernel_rel_path):
    """
    `protoprimer` entry script boilerplate function to import `proto_kernel`.
    """
    import os
    import importlib.util

    module_spec = importlib.util.spec_from_file_location(
        "proto_kernel",
        os.path.join(
            os.path.dirname(__file__),
            proto_kernel_rel_path,
        ),
    )
    loaded_proto_kernel = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(loaded_proto_kernel)
    return loaded_proto_kernel


proto_kernel = import_proto_kernel("../../../cmd/proto_code/proto_kernel.py")
__version__ = proto_kernel.__version__


# -- Project information

project = "protoprimer"

# any `X.Y.Z.devN`:
release = __version__
# only `X.Y`:
version = ".".join(release.split(".")[:2])

# -- General configuration

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinxcontrib.googleanalytics",
    "sphinxcontrib.mermaid",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
}
intersphinx_disabled_domains = ["std"]

templates_path = ["_templates"]

exclude_patterns = []

if is_full_protoprimer_content:
    exclude_patterns.append("stub/")
else:
    exclude_patterns.append("full/")

base_url = "https://protoprimer.readthedocs.io"

# Get the version name (e.g., "latest", "stable", "v1.0"):
rtd_version_name = os.environ.get("READTHEDOCS_VERSION")

# The URL structure configured in the `protoprimer` project:
html_baseurl = f"{base_url}/{rtd_version_name}/"

# -- Options for HTML output

# html_theme = "sphinx_rtd_theme"
# html_theme = "alabaster"
html_theme = "alabaster"

# -- Options for EPUB output
epub_show_urls = "footnote"

root_doc = "index"

html_show_copyright = False

googleanalytics_id = "G-7359VQM37J"

# Set this to `False` to hide the "View page source" link:
html_show_sourcelink = False

github_url = "https://github.com/uvsmtid/protoprimer"

html_context = {
    # Integrate GitHub for `html_theme = "sphinx_rtd_theme"`:
    "display_github": True,
    "github_user": "uvsmtid",
    "github_repo": "protoprimer",
    "github_version": "main",
    "conf_py_path": "/doc/readthedocs/source/",
}

html_theme_options = {
    # Integrate GitHub for `html_theme = "alabaster"`:
    "github_user": "uvsmtid",
    "github_repo": "protoprimer",
    "github_banner": True,
    # ===
    # If using `sphinx_rtd_theme`:
    "collapse_navigation": False,
    # If `True`, the navigation menu stays visible when page is scrolled:
    "sticky_navigation": True,
    # How many levels down should be shown:
    "navigation_depth": 4,
    "includehidden": True,
    # Set to `False` to show sub-headings within pages:
    "titles_only": False,
    # Options: "bottom", "top", "both", or `None`:
    "prev_next_buttons_location": "both",
    "version_selector": True,
    "language_selector": False,
}

html_sidebars = {
    # This removes all sidebar elements for `stub` mode and `html_theme = "alabaster"`:
    "**": [],
}
