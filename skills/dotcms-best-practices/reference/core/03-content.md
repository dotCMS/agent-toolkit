# 03 · Content (contentlets)

Creating and publishing content items.

**How content is created: you fire an ACTION on a contentlet.** There is no "create content" call — you fire a workflow *action* (a system action like `PUBLISH`, `NEW`, `EDIT`) and the contentlet is the target it acts on. The action is the verb; the contentlet is the payload. So "publish this content" = "fire the PUBLISH action with this contentlet in the body." Use **`PUT`** on the fire endpoint (`PUT /api/v1/workflow/actions/default/fire/PUBLISH`) — `POST` may return no identifier even when it half-creates the record. (Pages are the same pattern — a page is a contentlet of an HTMLPAGE type — but you create those with the `page_create` tool, see [04-pages.md](04-pages.md).)

## Content is stored per site — pass `contentHost` on every contentlet

Set `contentHost: <siteId>` via the Site-or-Folder field the type must have ([02-content-types.md](02-content-types.md)). Skip it and the contentlet saves onto the wrong site with `errors: []` and `live: true`, then URL-mapped detail routes 404 even though the content clearly exists.

Host-scope listing queries too, or another site's content renders as yours:

```velocity
#set($awzHost = $host)
#set($q = "+contentType:Book +live:true +conHost:${awzHost.identifier}")
```

## Field keys are the exact field VARIABLE — casing matters
The `contentlet` in the action body is keyed by each field's `variable`. Wrong case is silently ignored, then the field 400s as "required". Read the real names first: `GET /api/v1/contenttype/id/{idOrVar}` → `entity.fields[].variable`.

## Use `indexPolicy=WAIT_FOR` when chaining or reading right after firing an action
Fire the PUBLISH action via `PUT /api/v1/workflow/actions/default/fire/PUBLISH?indexPolicy=WAIT_FOR` with `{contentlet:{...}}`. Use `WAIT_FOR` on every action another step depends on — `DEFER` (default) may lag and a follow-up read can return stale data. `FORCE` is expensive — debugging only.

## Read a contentlet back by identifier at the right path
`GET /api/v1/content/{identifier}` (or `POST /api/content/_search`). NOT `/api/v1/content/id/{id}`.

## Workflow

### There is NO endpoint to associate a scheme to a content type
`POST /workflow/schemes/{id}/contenttypes/...` etc. all 404/405. The only way in is the
`workflow: ["<schemeId>"]` array on the **content-type create body** (spec:
`ContentTypeRequestView`) — so associate the scheme when you create the type
([02-content-types.md](02-content-types.md)); retrofitting it means recreating the type.

The System Workflow is often reachable without an explicit association, but don't build
on that: associate it in the create body and `PUT /api/v1/workflow/actions/default/fire/PUBLISH`
is guaranteed to have an action to fire.

### Firing a specific action by UUID vs. a system action by name
The `/default/fire/{systemAction}` endpoints take the system-action *name* (`NEW`, `EDIT`, `PUBLISH`, …). The other fire endpoints take a workflow *action UUID* — not the enum name. Get the UUID from `GET /api/v1/workflow/contentlet/{inode}/actions` (or `.../contenttypes/{var}/system/actions` without an inode).

## Assets & uploads

### `assets` is a RESERVED top-level folder
Uploading to `//<host>/assets/...` → `reserved folder name: assets`. Put themes/VTL/containers under `/application` (e.g. `//<host>/application/themes/<name>`), or use `/images`, or another non-reserved path. `/dA/` URLs are host-portable by identifier.

### `upload_assets` booleans accept string forms now
`verify` / `publish` accept `true/false` (bool) and `"true"/"false"/"1"/"0"` (string) — the tool coerces them. Prefer real booleans; omit `verify` to accept its default.
