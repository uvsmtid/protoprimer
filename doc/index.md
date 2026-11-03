---
# The site root is this redirect page: crawlers (link previews) do not follow the redirect, so repeat the `intro` metadata here:
seo_title: protoprimer - bootstrap a repo clone with one command
myst:
  html_meta:
    "robots": "noindex, follow"
    "description": "protoprimer is an arg-less one-liner to bootstrap isolated repo clones with environment-specific config: no setup manuals for your users."
---

% Redirect to "intro":
```{raw} html
<meta http-equiv="refresh" content="0; url=intro.html">
<script>window.location.replace("intro.html");</script>
```

% Custom `Intro` name for navigation side-bar (no `:titlesonly:` to show its sections):
```{toctree}
:hidden:
:maxdepth: 2

Intro <intro>
```

```{toctree}
:hidden:
:maxdepth: 2
:titlesonly:

Background <background>
Tutorial <tutorial_overview>
Config <config>
Reference <reference>
Dictionary <dictionary>
Alternative <alternative>
```
