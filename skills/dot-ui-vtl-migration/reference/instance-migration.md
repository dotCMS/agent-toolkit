# Migrate a whole instance

Use this when the user asks to migrate **all** custom fields, every legacy field, or "the whole
instance", not a single pasted VTL file. The `dotcms` MCP server does the I/O; the agent migrates
each file in between, in the default **inline** mode (see `SKILL.md` → Output Modes).

Enumerate the MCP server's tools and read their descriptions; each description is the source of
truth for how to call it. Discover endpoints by searching the spec first. Use the purpose-built
asset-transfer tools for files, so the code never passes through your context.

## Ground rules

- **Work in batches the customer picks.** Never migrate and publish the whole instance in one go
  unless they ask for it.
- **Nothing is written to the instance until the customer has confirmed** the summary of changes
  (step 5), and a dry run (step 6) has been shown.
- **One bad item never blocks the batch.** Record it as `skipped` or `failed` with the reason,
  and carry on.
- **Credentials belong to the MCP server.** Never ask for, read, or write a token.

## Working directory

Keep everything under one directory, `./vtl-migration/`, and never commit it:

```
vtl-migration/
  manifest.json
  original/assets/<id>__<fileName>     downloaded /dA/ file
  original/fields/<Type.field>.vtl     in-field VTL
  migrated/...                         same relative paths as original/
```

`manifest.json` is yours to maintain. One entry per thing to change:

| `kind` | Meaning | Key fields |
|---|---|---|
| `asset` | A file loaded by `#dotParse("/dA/<id>")` | `key` = identifier, `inode`, `languageId`, `contentType`, `binaryField`, `fileName`, `usedBy`, `file` |
| `field` | VTL stored in the custom field itself | `key` = `Type.field`, `typeId`, `fieldId`, `file` |
| `renderMode` | A field that only needs the switch to **Recommended** | `key` = `Type.field`, `typeId`, `fieldId`, `requires` (asset keys that must be published first) |

Every entry has `status`: `pending`, `published`, `skipped` or `failed`, plus a `statusReason`.
Record the instance URL in the manifest; if it differs from the instance the MCP server is
connected to now, stop and ask.

## 1. Discover

List every content type, then fetch each one in full. Look only at fields whose class is
`com.dotcms.contenttype.model.field.ImmutableCustomField`, and read the field's `values` (its
VTL). Classify each field, in this order:

| Finding in `values` | Category | Action |
|---|---|---|
| One or more `#dotParse("/dA/<id>")` | Downloadable file | Resolve it (below); queue if legacy |
| `#dotParse` of any other path | Unhandled path | Report only |
| `$velutil.mergeTemplate('...')` or `#parse('...')` | Core-shipped file | Report only; the file ships inside dotCMS |
| Contains `isNewEditModeEnabled` | Already migrated | Report only; queue a `renderMode` entry if the field is not in Recommended mode |
| Contains `dojo.`, `dijit`, `dojoType` or `DotCustomFieldApi.get/set/onChangeField(` | In-field legacy VTL | Queue as a `field` entry |
| None of the above | Already fine | Nothing to do |

Resolving a `/dA/<id>` reference: `GET /api/v1/content/<id>`.

- No content, or no binary field (`asset`, `fileAsset`, or the variable before `ContentAsset`
  in the response) → **unresolved**, report it.
- The returned `identifier` differs from `<id>` → the field **pins a specific version** (an
  inode). Report only; publishing always lands on the latest version of the identifier, so this
  cannot be migrated safely. Tell the customer to point the field at the identifier.
- The file already contains `isNewEditModeEnabled` → already migrated, report only.
- No file name (`fileName`, `name`, `title`) → unresolved.
- Otherwise queue an `asset` entry. Note when the content is not `live`.

A `renderMode` entry is queued for a field that is not yet in Recommended mode (no field
variable `newRenderMode` = `component`) when its code is, or after publishing will be,
migrated: owners of a queued or already-migrated `/dA/` asset (list the queued assets in
`requires`), and fields whose inline code already carries the switch. Skip a field that also
uses an unhandled path, an unresolved asset or a pinned version: flagging it would switch
unmigrated code to the new editor. An in-field legacy entry needs no `renderMode` entry; the
flag goes in the same update as its code.

## 2. Download

Download each queued `asset` into `original/assets/` with the asset-download tool. It takes a
dotCMS path, so resolve the identifier to a path first (the content's `path`/`url` and its
host). Write each in-field VTL to `original/fields/` exactly as stored. Record `inode` (assets)
or keep the original text (fields): these are your conflict check in step 6.

Re-running discovery after a publish should not download again what is already migrated: when an
asset's current `inode` equals the one recorded as migrated, skip the download.

## 3. Show what's pending and let the customer pick

One numbered table, nothing migrated yet:

| # | VTL | Kind | Used by |
|---|---|---|---|
| 1 | `text-count.vtl` | `/dA/` file | 5 fields: `Destination.pageTitleCount`, … |
| 2 | `Banner.widget` | inline field | `Banner.widget` |

List `renderMode` entries with an empty `requires` as one extra row ("Switch to Recommended
only: …"). Do not list those with `requires`: they go along with their asset. Sum up report-only
buckets in one line of counts ("25 load core files, 3 use unhandled paths, say *details* to see
them"). Ask which rows to do now: `all`, row numbers (`1,3`) or `none`, and wait.

## 4. Migrate the selected files

Migrate each selected file in `original/` in the default inline mode and write the result to
`migrated/` under the same relative path. When assembling the file, copy the legacy bytes with
the shell recipe in `SKILL.md` (Mode 1); never retype them.

## 5. Confirm

Summarize what changed per file and get the customer's explicit confirmation before touching the
instance.

## 6. Dry run, then publish only that batch

Process entries in manifest order, so assets come before the `renderMode` entries that depend on
them. For each selected entry, run the checks, and with a dry run report the outcome without
writing. Show the dry run, then repeat it for real.

**Per-entry checks (all must pass, otherwise `skipped` with the reason):**

1. **Unchanged since download.** Re-read it now. An asset: `GET /api/v1/content/<identifier>`
   and its `inode` equals the recorded one. A field:
   `GET /api/v1/contenttype/<typeId>/fields/id/<fieldId>` and its `values` equal the original
   text byte for byte.
2. **Genuine inline migration.** The migrated file starts with
   `#if( $structures.isNewEditModeEnabled() )` on line 1, and the text after the top-level
   `#else` up to the final `#end` is the original, verbatim. Also pass the "Before emitting
   inline" checks in `SKILL.md`. A migrated file that fails is skipped, never "fixed" here.
3. **Dependencies met** (`renderMode`): every asset in `requires` is `published`, or the entry
   is `waiting` and stays `pending`.

**Writes:**

- **`asset`**: fire the `PUBLISH` workflow action on the existing identifier with the migrated
  file as the binary field (multipart: a `json` part with `contentlet.contentType`,
  `contentlet.identifier` and `binaryFields: [<binaryField>]`, and the file under its original
  `fileName`), with `language` = the entry's `languageId` and `indexPolicy=WAIT_FOR`. The
  identifier must stay the same, so `#dotParse("/dA/<id>")` keeps working. Take the new `inode`
  from the response; if it cannot be read, report `failed` and ask the customer to verify, never
  `published`.
- **`field`**: save the full field with the migrated `values` **and** `newRenderMode` =
  `component` in one `PUT /api/v3/contenttype/<typeId>/fields/<fieldId>` (body
  `{ "field": <full field> }`). The v3 update rebuilds the field and replaces the variables list
  wholesale, so send the field exactly as fetched, with every other field variable kept; an
  omitted variable is deleted. Keep the existing `newRenderMode` variable's id if there is one.
- **`renderMode`**: the same v3 update, changing only that variable. Skip if already
  `component`.

A migrated field only renders natively in the new editor once it is in Recommended mode.

## 7. Report and offer the next batch

Say what was published, skipped (and why), failed or is waiting, name the fields that were
switched to Recommended, then show what is still `pending` and ask whether to continue.
Unselected rows stay pending; nothing is lost by stopping. Never re-publish an entry that already
finished (`published`, `skipped`, `failed`) unless the customer names it to retry. In a later
session start again from step 1: discovery lists only what is left.
