---
myst:
  html_meta:
    "robots": "noindex, follow"
---

% Redirect to "intro":
```{raw} html
<meta http-equiv="refresh" content="0; url=intro.html">
<script>window.location.replace("intro.html");</script>
```

% Custom `Intro` name for navigation side-bar:
```{toctree}
:hidden:
:maxdepth: 2
:titlesonly:

Intro <intro>
Background <background>
Tutorial <tutorial_overview>
Config <config>
Reference <reference>
Alternatives <alternatives>
```
