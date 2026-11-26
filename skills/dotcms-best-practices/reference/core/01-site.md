# 01 · The site

**First build step, both delivery modes.** Everything after this needs the site's identifier: content types scope content to it, assets upload into its folder tree, the template payload carries `siteId`, and pages are created under it. Create it before anything else.

You need a hostname before starting — from PLAN.md §2 if you came from `dotcms-create-sites`, otherwise ask for it; never invent one. Sites have no purpose-built tool — go through the dotCMS MCP server.

## Create (or reuse) the site

Look it up by hostname first so a re-run doesn't fail or duplicate:

```
GET  /api/v1/site?per_page=100&archive=false   → match entity[].hostname
POST /api/v1/site                  → { "siteName": "<hostname>", "description": "…", "languageId": 1 }
```

The created site's `identifier` is what every later step means by "site id".

- **`per_page`, not `perPage`.** dotCMS ignores `perPage` and returns its default page of 10 sites, so a lookup on a larger instance misses sites.
- **`archive=false` includes unpublished sites.** Without it the listing skips them, so a re-run doesn't find the unpublished site it created the first time. (`archive=true` returns only archived sites.)

## Set aliases, then publish

A new site is **unpublished** — it serves nothing until you publish it. Aliases are set with a separate `PUT`, which has two traps:

```
PUT /api/v1/site?id=<siteId>       → { "siteName": "<hostname>", "aliases": "<alias>", "forceExecution": true }
PUT /api/v1/site/<siteId>/_publish
```

- **The id goes in the query string.** An `identifier` in the body is ignored.
- **`siteName` is mandatory on the PUT** even when you are only changing aliases; omit it and the call fails.
- **`forceExecution: true`** is required for the change to apply.

## Give it a `*.localhost` alias for verification

Verification requests resolve the site by **hostname**, and a fetch client cannot fake one: Node's `fetch` silently drops a `Host` header (the Fetch spec forbids it), so the request lands on the *default* site and every check 404s while the pages are actually fine.

Set an alias ending in `.localhost` — e.g. `mysite.localhost` for the site `mysite.local`. Browsers and Node resolve `*.localhost` to `127.0.0.1` with no `/etc/hosts` entry, so `http://mysite.localhost:8080/` reaches the right site. Verify against the alias, not the canonical hostname.

## Folders and the menu

The menu comes from the Navigation API: `$navtool.getNav()` in VTL, `GET /api/v1/nav/<path>` over REST. It lists the folders and pages under a path that have **Show on Menu** on, ordered by **Sort Order** and labelled with their **Title**. A folder created with default settings has none of these, so it is left out, the menu renders empty, and the page still returns HTTP 200.

Read a menu, the model site's or your own, with the Navigation API:

```
GET /api/v1/nav/?depth=2&host_id=<siteId>   → entity.children[]: title, order, href
```

- **`depth=2`.** `depth=1` returns only the starting folder, with no children.
- **`host_id`.** Without it the API resolves the request's site and returns the System folder.
- **It works on unpublished sites,** so you can check a new site's menu before anything is published.

The Navigation API is read only. To put a folder on the menu, set its title, Show on Menu and Sort Order when you create it, or fix an existing folder, with the assets endpoint:

```
POST /api/v1/assets/folders   → { "assetPath": "//<hostname>/offers/", "data": { "title": "Offers", "showOnMenu": true, "sortOrder": 1 } }
PUT  /api/v1/assets/folders   → same body, for a folder that already exists
```

- **`POST /api/v1/folder/createfolders/{siteName}` creates folders with default settings only,** and `/api/v1/folder` has no update.
- **It may not show up when you search the API spec.** Call it directly with the execute tool.
- **`assetPath` is host-qualified and ends with `/`.**
- **Copying an existing site?** Read its menu with the Navigation API and create the same folders with the same title and order.
- **Folder titles have no language.** The title is the same in every language; a translated menu label has to come from the theme or from a page title.

## Done when

`GET /api/v1/site?per_page=100&archive=false` shows the site with your hostname, its alias set, and `http://<alias>:8080/` returns something other than the default site, and `GET /api/v1/nav/?depth=2&host_id=<siteId>` lists the menu you expect, in order. Record the identifier — [02](02-content-types.md) onward all need it.
