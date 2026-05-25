
% [TODO: either use `draft_doc/index.md` or `final_doc/index.md` manually depending on `is_draft_doc_protoprimer_content`]
% DISABLED: include:: draft_doc/index.md
% DISABLED: include:: final_doc/index.md

% Redirect to "intro":
```{raw} html
<meta http-equiv="refresh" content="0; url=final_doc/intro.html">
<script>window.location.replace("final_doc/intro.html");</script>
```

% Custom `Intro` name for navigation side-bar:
```{toctree}
:hidden:
:maxdepth: 1

Intro <final_doc/intro>
reference
```
