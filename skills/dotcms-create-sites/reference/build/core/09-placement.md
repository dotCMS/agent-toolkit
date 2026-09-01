# 09 · Placement (put content into page slots)

Place content with the `page_place_content` tool — its description is the source of truth for how to call it (slot addressing, `append`/`set`/`remove` ops, `merge`/`replace` modes, the full-replace footgun it absorbs, the returned manifest). This file only covers where it fits in the build.

- **When:** after the template's layout is set and published ([05-templates.md](05-templates.md)) and after `page_create` (which leaves the page blank).
- **Don't hand-roll it.** The raw `POST /api/v1/page/{pageId}/content` is a full replacement that wipes every slot you omit; `page_place_content` merges safely. Don't reach for `execute` here.
- **Then re-publish the page.** Placement updates the page's WORKING content map; LIVE doesn't change until you publish the page (fire PUBLISH). See the publish rules in [00-what-must-exist.md](00-what-must-exist.md).

Placement can succeed and still render empty — verify per your delivery mode:
[vtl/05](../vtl/05-verify-and-debug.md) or [nextjs/05](../nextjs/05-verify.md).
