# 04 · Pages

Create pages with the `page_create` tool; its description covers what it handles (folder creation, required-field validation, the URL-collapse trap, `cacheTtl`, root page). You do not fire the action by hand or pre-create folders — the tool does both. (Under the hood a page is a contentlet of an HTMLPAGE type, created by firing an action on it — see [03-content.md](03-content.md) — but `page_create` wraps all of that.)

One thing to remember from its description: **`page_create` leaves the page live but BLANK.** Placing content on it is a separate step — see [09-placement.md](09-placement.md).
