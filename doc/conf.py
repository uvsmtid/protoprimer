# Configuration file for the Sphinx documentation builder.
import os
import re

from docutils import nodes

# TODO: This is a temporary option to have a basic `readthedocs` page while the rest of the docs are in progress.
#       When changed here, it should also be changed in `./index.rst` (automation did not work):
is_draft_doc_protoprimer_content = False
doc_tag_name: str
if is_draft_doc_protoprimer_content:
    doc_tag_name = "protoprimer_draft_doc"
else:
    doc_tag_name = "protoprimer_final_doc"
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


proto_kernel = import_proto_kernel("../cmd/proto_code/proto_kernel.py")
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
    "sphinx_sitemap",
]

myst_fence_as_directive = [
    "mermaid",
]

mermaid_init_config = {
    "look": "handDrawn",
}
mermaid_light_theme = "neutral"

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

exclude_patterns = [
    "untracked_notes/**",
    "task_ref/**",
    "dev_note/**",
    "readme.md",
]

if not is_draft_doc_protoprimer_content:
    exclude_patterns.append("draft_doc/**")

base_url = "https://protoprimer.readthedocs.io"

# `READTHEDOCS_CANONICAL_URL` reflects the URL versioning scheme configured in the project settings:
# * `multiple_versions_with_translations` (includes language, e.g. `.../en/latest/`)
# * `multiple_versions_without_translations` (e.g. `.../latest/`)
rtd_canonical_url = os.environ.get("READTHEDOCS_CANONICAL_URL")

# Fallback to `local` for local builds — `sphinx-sitemap` requires non-empty value:
html_baseurl = rtd_canonical_url or f"{base_url}/local/"

# Default `sitemap_url_scheme` is `"{lang}{version}{link}"`.
# Using "{link}"` page path only that `sphinx-sitemap` appends to `html_baseurl`:
sitemap_url_scheme = "{link}"

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
    "conf_py_path": "/doc/",
}

html_theme_options = {
    # Integrate GitHub for `html_theme = "alabaster"`:
    "github_user": "uvsmtid",
    "github_repo": "protoprimer",
    "github_banner": False,
    "fixed_sidebar": True,
    "page_width": "1200px",
}

html_sidebars = {
    "**": [
        "navigation.html",
    ],
}

# Matches tag prefixes like `FT_00_00_00_00` or `UC_00_00_00_00` at start of title.
_TAGGED_TITLE_RE = re.compile(r"^[A-Z]+_\d+_\d+_\d+_\d+\.")


def _strip_tag_prefix(text: str) -> str:
    # Remove leading tag like `FT_00_00_00_00` or `UC_00_00_00_00` from a title string.
    return _TAGGED_TITLE_RE.sub("", text)


def _on_doctree_resolved(
    app,
    doctree,
    docname,
):
    # Strip tag prefix from the first title node (page <h1>).
    # Fires after `toctree` has already captured `env.titles`,
    # so `reference.html` listings keep the full prefixed title
    # while the individual page shows only the suffix
    # (e.g. `some_name` instead of `FT_00_00_00_00.some_name`).
    for node in doctree.traverse(nodes.title):
        raw = node.astext()
        stripped = _strip_tag_prefix(raw)
        if stripped != raw:
            node.clear()
            node += nodes.Text(stripped)
        break


def _on_html_page_context(
    app,
    pagename,
    templatename,
    context,
    doctree,
):
    # Strip tag prefix from `context["title"]`
    # so the browser tab title matches the stripped <h1> set by `_on_doctree_resolved`.
    if "title" in context:
        context["title"] = _strip_tag_prefix(context["title"])


def setup(app):
    app.connect("doctree-resolved", _on_doctree_resolved)
    app.connect("html-page-context", _on_html_page_context)
