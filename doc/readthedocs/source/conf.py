# Configuration file for the Sphinx documentation builder.
import os

# TODO: This is a temporary option to have a basic `readthedocs` page while the rest of the docs are in progress.
#       When changed here, it should also be changed in `./index.rst` (automation did not work):
is_full_protoprimer_content = False
doc_tag_name: str
if is_full_protoprimer_content:
    doc_tag_name = "protoprimer_full"
else:
    doc_tag_name = "protoprimer_stub"
# NOTE: `tags` are not supposed to be `import`-ed:
tags.add(doc_tag_name)


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
html_title = "bootstrap repo env"

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
    "myst_parser",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
}
intersphinx_disabled_domains = ["std"]

templates_path = ["_templates"]

html_extra_path = [
    "BingSiteAuth.xml",
]

exclude_patterns = []

if is_full_protoprimer_content:
    exclude_patterns.append("stub/")
else:
    exclude_patterns.append("full/")

base_url = "https://protoprimer.readthedocs.io"

# `READTHEDOCS_CANONICAL_URL` reflects the URL versioning scheme configured in the project settings:
# * `multiple_versions_with_translations` (includes language, e.g. `.../en/latest/`)
# * `multiple_versions_without_translations` (e.g. `.../latest/`)
rtd_canonical_url = os.environ.get("READTHEDOCS_CANONICAL_URL")

# The URL structure configured in the `protoprimer` project:
html_baseurl = rtd_canonical_url

# -- Options for HTML output

# html_theme = "sphinx_rtd_theme"
# html_theme = "alabaster"
html_theme = "alabaster"

html_static_path = ["_static"]

html_css_files = ["custom.css"]

# -- Options for EPUB output
epub_show_urls = "footnote"

root_doc = "index"

html_show_copyright = False
html_show_sphinx = False

googleanalytics_id = "G-7359VQM37J"

# Set this to `False` to hide the "View page source" link:
html_show_sourcelink = False

# Do not replace `...` with a single char:
smartquotes = False

github_url = "https://github.com/uvsmtid/protoprimer"

html_favicon = "_static/protoprimer.logo.16x16.png"

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
    "github_banner": False,
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
