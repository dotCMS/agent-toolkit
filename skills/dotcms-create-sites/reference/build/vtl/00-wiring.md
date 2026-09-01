# 00 · VTL wiring

In addition to [core/00](../core/00-what-must-exist.md), a VTL-rendered page needs:

1. **Template → theme.** The theme's `template.vtl` must loop `$dotThemeLayout`;
   without that loop the page is a bare shell whatever you place ([02](02-themes.md)).
2. **Container → non-empty `preloop.vtl`/`postloop.vtl` + one `<Var>.vtl` per content
   type**, filename = the type's Velocity variable, case-exact ([03](03-containers.md)).
3. **Each item renders through the right mechanism** — content section, widget or
   detail page ([01](01-choose-mechanism.md)). Wrong mechanism renders empty.

Verify in LIVE ([05](05-verify-and-debug.md)). A VTL error is swallowed into an empty
string with HTTP 200, so "no error" is not evidence that anything rendered.
