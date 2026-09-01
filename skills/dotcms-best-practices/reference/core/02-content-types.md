# 02 · Content types & fields

Creating the content types (data types + editable-section types) and their fields.

There is no dedicated MCP tool for content types — go through `execute`, the same as sites
([01](01-site.md)).

The content-type create body, its `fields[]` array (field `clazz` values, `dataType` mapping, boolean-via-RadioField, Story Block, the `workflow` key, row/column layout), the `type=` base-type filter, and fetch-by-id are all documented in the OpenAPI spec — read them with the `search` tool (`spec.paths['/api/v1/contenttype']`, schema `ContentTypeRequestView`). This file keeps only what the spec can't express.

## Every type needs a Site-or-Folder field and a workflow

Set both in the create body. Each has a silent failure mode, and neither is convenient to add afterwards.

**Site-or-Folder field** — this is what lets content be stored *per site*. Without it the site cannot be set when content is created: `contentHost` / `host` / `hostFolder` in the fire body are ignored silently (the response still says `errors: []`, `live: true`), the contentlet lands on the wrong site, and URL-mapped detail routes 404. Give it the variable `contentHost`:

```json
{ "clazz": "HOST_OR_FOLDER", "name": "Site", "variable": "contentHost", "required": true, "indexed": true }
```

**Workflow** — associate a scheme with the `workflow` array. There is no endpoint to
attach one to an existing type ([03-content.md](03-content.md)), so getting this wrong
means recreating the type. The System Workflow is the safe default.

**Always fetch the id — never hardcode it.** `GET /api/v1/workflow/schemes` and read the id of
the scheme you want; ids are not guaranteed to be the same across installs.

```json
{ "workflow": ["<id from GET /api/v1/workflow/schemes>"] }
```

## The variable is derived, and you must read it back

**You do not choose the variable — dotCMS derives it from the name**, and the result may not
match what you'd guess. Two things to know:

- **A name collision appends a number.** Create `Testimonial` when a `Testimonial` already
  exists and the new type's variable becomes `testimonial1`. The create still succeeds.
- **Casing is not guaranteed to follow the name.**

The variable is the key everything else matches on, case-exact — a container's `<Var>.vtl`
filename ([vtl/03](../vtl/03-containers.md)) and a headless component-map key
([nextjs/01](../nextjs/01-component-contract.md)). So **after creating a type, read the variable
back off the response or fetch the type, and use that value.** Assuming it equals the name is
the cause of a whole class of silent blank renders.

## Reserved variable names
Variable names must match `[_A-Za-z][_0-9A-Za-z]*` (start with a letter or `_`, then only letters/digits/underscores — no spaces, no leading digit, no special characters). The words below are not allowed; matching is case-insensitive. If you need one, prefix it: `Host` → `AwazonHost`, field `type` → `productType`.

**Not allowed as a content-type variable:** `host`, `conhost`, `conhostname`, `contenttype`, `basetype`, `structurename`, `structuretype`, `title`, `type`, `tags`, `categories`, `inode`, `shortinode`, `identifier`, `shortid`, `urlmap`, `path`, `parentpath`, `owner`, `ownercanpublish`, `ownercanread`, `ownercanwrite`, `moddate`, `moduser`, `pubdate`, `expdate`, `recurrencestart`, `recurrenceend`, `originalstartdate`, `live`, `working`, `deleted`, `locked`, `languageid`, `permissions`, `metadata`, `versionts`, `wfassign`, `wfcreatedby`, `wfcurrentstepname`, `wfmoddate`, `wfscheme`, `wfstep`. Plus, for brand-new types only: `folder`, `file`, `forms`, `htmlpage`, `menulink`, `container`, `template`, `user`, `calendarEvent`.

**Not allowed as a field variable** (a different list): `languageid`, `locked`, `live`, `moddate`, `identifier`, `host`, `class`, `confolder`, `conhost`, `deleted`, `file`, `form`, `inode`, `moduser`, `owner`, `number`, `string`, `ownercanpublish`, `ownercanwrite`, `ownercanread`, `permissions`, `type`, `website`, `working`, `stinode`, `disabledwysiwyg`, `archived`, `basetype`, `contenttype`, `modusername`, `ownerusername`, `creationdate`, `publishuser`, `publishusername`. A field variable is also rejected if it collides with an inherited GraphQL field of an incompatible type.

## Adding fields
Create the type with its fields inline as `fields[]` in the content-type POST — one call, and the spec documents the body (`ContentTypeRequestView`). To change fields on an existing type, use the **v3** fields endpoints under `/api/v3/contenttype/{typeIdOrVarName}/fields` (GET the layout, `PUT .../fields/move` to add/move a field, `PUT .../fields/{id}` to update one, DELETE to remove) — all in the spec; read them with `search`. The **v1** `/api/v1/contenttype/{typeId}/fields` endpoint is deprecated — don't use it (it had a trap where POSTing an array silently saved only the first field).

## WIDGET types: `widgetCode` belongs to the TYPE
Creating a `WIDGET` base type auto-adds `widgetTitle`, `widgetUsage`, `widgetPreexecute` and `widgetCode`. `widgetCode` is a **constant field**: its value lives on the field of the content type and is shared by every contentlet of that type — it is not a per-contentlet value, and a `widgetCode` key in a contentlet body does nothing.

Build consequence: a widget's code is set as part of **building the type**, not part of creating the content. Set the field's `values` (inline in the create body, or via the v3 fields endpoints above). A widget's *author-set* fields — heading, limit, category — are ordinary per-contentlet values; only the constant fields behave this way.

## URL-mapped types (detail pages) — two more keys, set AFTER the page exists

If this type drives a detail page, it needs both of these on the type, in **either**
delivery mode:

- `urlMapPattern` — the URL shape with a slug token, e.g. `/products/{urlTitle}`
- `detailPage` — the **identifier of the page** that renders it

The token must name a real field on the type whose value is the slug, **unique per
item** and indexed. Add that field here; `detailPage` you cannot set yet, because the
page it identifies does not exist until [04](04-pages.md). Create the type now, create
the page, then PUT/PATCH these two keys onto the type.

Rendering the resolved item is mode-specific: VTL reads `$URLMapContent`
([vtl/04](../vtl/04-listings-and-details.md) Recipe B), headless reads `urlContentMap`
([nextjs/04](../nextjs/04-listings-and-details.md)).
