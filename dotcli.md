# dotCLI MVP — Greenfield Spec

**Date:** 2026-08-26
**Author:** Freddy Montes
**Input from:** Laura Cabrerizo, Miller Gonzalez, Ian Cooper, Scott Wicken
**Status:** Decided — ready to build
**Pillar:** [[developer-experience]]
**Supersedes:** Asana "dotCLI Enhancements" (1211880645437047)

---

## Part 1 — Decision record

### 1. What we're building

`@dotcms/dotcli`, bin `dotcli`. A new TypeScript CLI. No code from the current Java/Quarkus one, which is too hard to maintain and release. It moves files between a local folder and dotCMS. The local files are the source of truth. Git is optional. The mental model is git: pull, merge, push.

### 2. The problem, corrected

Developers stay on WebDAV because they don't trust the CLI. The loudest reason in the thread — "the CLI overwrites other people's work" — is real, but it is not a CLI regression. WebDAV has no working locks either; Scott's read of the code is that they are "ceremonial." Laura believed WebDAV was a constant sync. It never was.

The real gaps:

- No drift detection. Push overwrites whatever the server has.
- No conflict resolution. The second pusher wins and the first pusher's work is gone. This happened on a concierge-development account: two developers pushed the same files and the first one's work was lost.
- `files push --removeFolders` deletes remote folders that are missing locally. The local tree cannot represent pages or content, so it deleted folders that held pages (Miller).
- The `working/` and `live/` folder split confuses people (Laura, Miller).

### 3. The four invariants

Break one and this is a different product.

1. **Push never deletes.** Absence is never read as intent. Removing from dotCMS is `dotcli rm`.
2. **Push is always draft.** It creates a working version. Nothing goes live without `dotcli publish`.
3. **Push is rejected if the remote moved** since your last pull. Pull, merge, push.
4. **Publish always fires the mapped workflow action** and honors permissions. Never the raw publish endpoint.

### 4. Scope

|  |  |
|---|---|
| **In** | FileAssets: `.vtl`, `.js`, `.css`, `.html`, `.svg`, images, fonts, any binary kept in the repo |
|  | File-based templates and containers — these are files; the CLI needs no knowledge of what they are |
| **Out** | Content types, languages, sites-as-objects, pages, contentlets |
|  | DB-only templates and containers. Never read, never written |

Because the only object is a file, identity is the path. No UUID mapping, no cross-environment key matching, no schema migration, no dependency graph. That is what makes this buildable in one pass.

### 5. What this does not solve

- The lost-work incident that justified this project included content type work. This covers the file half. Nobody should read "new dotCLI" as "that gap is closed."
- WebDAV mounts as a filesystem, so any application can save into it. The CLI cannot. Content Drive covers drag-and-drop for non-developers. Mounting is lost with no replacement, which ends the rclone-over-WebDAV workflow some developers rely on today.
- There is no undo for a bad merge. Git is the recovery path; without git, a merge that goes wrong is unrecoverable. `pull` asks before it modifies anything. Tool-owned backups are deferred.
- CI has no drift detection (§8). A UI edit to a code file on prod will be overwritten by the next deploy. The rule to document: prod is deployed from git, and editing code files in the prod UI is unsupported.

---

## Part 2 — Build spec

Terminal walkthroughs of these flows: [[dotcli-use-cases]].

### 6. Workspace layout

```
myproject/
  .dotcliignore
  .dotcli/                       # state, cached base versions, config
  brand-a.com/
    application/vtl/search.vtl   # = //brand-a.com/application/vtl/search.vtl
  brand-b.com/
    application/...
```

- The path on disk is the dotCMS address. Nothing to configure and nowhere for a mapping to drift.
- **Site is always a path segment, never a flag. Environment is always a flag, never a path.** The same tree goes to dev and prod, so the environment cannot live in the path.
- `--env <url>`. The URL is the environment identity. The first `login` records it as the workspace default in `.dotcli/config.yml`; `--env` overrides.
- Token lives in the OS keychain, keyed by URL. Never in the repo. CI passes `DOTCMS_TOKEN`.
- `.dotcliignore` uses gitignore syntax and filters both directions. Asymmetric filtering recreates the "wrong folder" confusion. Defaults: `.dotcli/`, `.DS_Store`, `*.remote`.
- A bare `push` in a tree holding more than one site requires `--all`.

### 7. Commands

| Command | git | Behavior |
|---|---|---|
| `login --env <url>` | — | Interactive token flow. Stores in keychain. Records the workspace default |
| `sites` · `ls <path>` · `tree <path> [--depth n]` | — | Browse the remote before claiming anything |
| `pull <path>` | `clone` | Add a subtree locally. Shows file count and size first |
| `pull` | `pull` | Refresh what is on disk. Three-way merge into the working tree |
| `status` | `status` | Contacts the server. Local changes, remote changes, conflicts, locks |
| `diff [path]` | `diff` | Offline. Line diff against the cached base, never the current server. A clean `diff` does not mean "matches remote" — that is `status` |
| `push [path]` | `push` | Create and update only, as draft. Shows the change set before sending. Rejected if the remote moved |
| `push --force` | `push -f` | Overwrite without a base. Prints every replaced path and its prior version id. From a TTY it requires a typed confirmation; non-TTY proceeds on the flag |
| `rm <path>` | `rm` | Deletes locally and archives in dotCMS — reversible. Only files tracked in state. `--destroy` for permanent |
| `publish [path]` | — | Fire the mapped workflow action. Shows the plan first |
| `unlock <path>` | — | Break a lock, if permitted. Also the recovery tool for stale locks |
| `doctor [--env url]` | — | Check auth, token expiry, write and publish permission, and that a publish action is resolvable |

- **No staging, no commit.** The working tree is the state. Push sends the working tree. There is no local history to build, so an index buys nothing.
- **Push is additive at the storage layer.** Every push checks in a new version; the version it supersedes stays in dotCMS history. No push is unrecoverable, which is why plain `push` does not ask for confirmation — it prints what it sent. Rejecting a moved base is about sparing someone a trip through version history, not about preventing loss.
- **Prompts are TTY-only. Nothing ever waits for input in CI.** Without a TTY: reads and non-destructive writes (`pull`, `push`, `publish`) proceed; anything that archives or destroys (`rm`, `rm --destroy`) requires `--yes` and exits 1 without it. A conflicted file in a non-TTY run is an error, never a prompt.
- **A rejection carries the evidence, not an instruction to go look.** For every moved file `push` prints both sides — what changed on the server since your base, and what you are trying to send — plus who moved it and when. The choice between merging and sending the rest is made from that output. Requiring a second command to see the divergence is the gap that made people distrust the old tool.
- **Refusals are scoped to the paths you asked for, never the workspace.** A conflict in `brand-b.com` must not block `push //brand-a.com/application`. Within a push, files whose base moved are rejected and named; the rest go through. Git rejects a whole push because its unit is a commit — we have no commit, so per-file is both possible and kinder. The trade: a change spanning several files can land partly. Use git and CI when a change must ship atomically.
- Read-only commands (`sites`, `ls`, `tree`, `status`, `diff`, `doctor`) write no state.
- `pull` with no path in an empty tree errors and names the next step. It never discovers and downloads an instance on its own.
- Tracking is implicit: a folder on disk is tracked. There is no claim, adopt, or forget command.
- Retries are for 5xx and network errors only. A 4xx fails immediately — retrying a 400 to the limit only makes a pipeline fail slowly.

### 8. State and the merge base

`.dotcli/state/<normalized-url>.json`:

```json
{ "files": { "brand-a.com/application/vtl/search.vtl": { "versionId": "…", "hash": "…" } } }
```

- Keyed per environment URL. A base pulled from dev is never used against prod.
- Stores the dotCMS version id, so the base is re-fetchable from the server.
- Disposable cache. Gitignored, never committed — two developers committing state creates conflicts inside the conflict detector.
- **No state means no base, and no base means `push` cannot tell whether the remote moved.** It refuses and says to run `pull` first, or `--force`. Same rejection path as a moved base, no special case, no prompt. A wiped state file costs you one pull.
- **There is no undo for a bad merge in the MVP.** `pull` merges into files whose only copy may be on disk. With git, `git stash` and `git checkout` are the recovery path. Without git there is none, so `pull` names every file it will modify and, on a TTY, asks first. Tool-owned backups are v2 — see §5.
- CI runners have no state, so **CI cannot detect drift.** `push --force` is the CI path. Its overwrite manifest makes every change recoverable from dotCMS version history.

### 9. Deletion rules

Prior art: `poc-dotcli` findings, Jul 2026 — the current CLI archives a removed file but leaves the parent folder, so empty folders accumulate with no cleanup path and are cleared by hand in the admin panel.

- `rm <file>` deletes the local file and archives the remote asset. Reversible in dotCMS. `--destroy` for permanent. Deleting locally and archiving remotely must be the same act, or the verb lies about what it did.
- `rm <folder>` archives the tracked files under it, then removes the folder.
- **A folder is never auto-removed** when `rm` empties it. The CLI cannot see pages or content inside a folder, so "no tracked files left" is not "empty".
- **But it is never left silent either.** `status` reports folders that hold no tracked files, so an orphan is visible and one command from gone.
- **`rm <folder>` counts and names what it cannot manage before it acts.** A `drive/search` on the folder with all base types returns the pages and contentlets living there, so the prompt says "holds 2 items the CLI cannot see (1 page, 1 contentlet)" instead of leaving the user to guess why the folder stayed.
- **Deletions do not propagate through CI.** Pipelines only run `push`, and push never deletes, so a file removed from the repo stays in prod until someone runs `rm` against that environment. This is the price of invariant 1. `status --env <url>` makes the drift visible.

### 10. Conflict rules

- Text (`.vtl`, `.js`, `.css`, `.html`): three-way merge on pull. Non-overlapping hunks merge automatically. Overlapping hunks get git-standard conflict markers, so any editor already handles them.
- Binary: no merge. Keep the local file, write the remote beside it as `<name>.remote`, mark it conflicted.
- Push refuses while a file **in the requested path** is conflicted. Text is resolved by removing the markers, binary by deleting the `.remote` file.
- State records that a file was conflicted. On a TTY, `push` names it — "resolved since conflict" — and asks once, so a formatter that strips markers cannot quietly pass off an unresolved merge as done. This is the only confirmation plain `push` ever shows, and in a non-TTY run it is an error instead.

### 11. Publish and workflow actions

- `publish` resolves the mapped workflow action for the FileAsset content type and fires it.
- No mapped action or no permission: the file is not published and is reported. This does not fail the run by itself.
- A required review step is honored. The result is a third state, neither error nor success: "search.vtl → Pending Review, not live."
- Partial failure is a report, not a rollback: "40 pushed, 37 live, 3 pending." Exit non-zero. Published files stay published. dotCMS offers no transaction to roll back into.
- There is no `--force-publish`. The CLI cannot bypass a review step. The MCP server currently can, by calling the endpoint directly — separate ticket, same rule should apply.

### 12. Locks

- dotCMS requires checkout to write a contentlet, and FileAssets are contentlets. Push is lock, write, unlock, per file. Lock awareness is mechanical, not optional.
- `status` and `pull` show `lockedBy` and whether you have permission to break it.
- Push skips locked files, reports them, and continues. One lock never aborts a 400-file run.
- Breaking a lock is `dotcli unlock`, never a flag on push.
- A crashed push must release what it locked. Stale locks are a real failure mode of this design.

### 13. Exit codes

`0` success · `1` generic · `2` auth failed or token expired · `3` rejected, remote moved · `4` unresolved conflicts · `5` partial — files skipped, or pushed but not published · `6` permission denied. Every message names the fix: an expired token says `run dotcli login --env <url>`.

### 14. Autonomy boundary

**Agents decide alone:** command and flag naming, help text, output format, `.dotcli/` internals and serialization, which diff3 library, retry and concurrency policy, error wording, test strategy, `.dotcliignore` defaults.

**Freddy decides:** any new write path beyond push, rm, publish, lock, unlock; any exception to the four invariants; any change to what `--force` does or where it applies; adding an object type; anything that bypasses a workflow action or a permission check, including for admins.

### 15. Acceptance scenarios

| Scenario | Expected |
|---|---|
| Dev A pushes `search.vtl`. Dev B pushes with a base from before that push | Dev B is rejected. `pull` merges lines 1–10 with 7–15 and marks the overlap. Push succeeds once resolved |
| A developer deletes a local folder that holds remote pages, then pushes | Nothing is deleted. Report: "N files exist in dotCMS but not locally" |
| `dotcli rm //brand-a.com/application/old/` | Tracked files under that path are archived, then the folder is removed. Untracked remote content is untouched |
| `dotcli rm` on the last tracked file in a folder | File archived, folder left in place. `status` then lists it as holding no tracked files |
| CI runs `push --force` then `publish` against prod | Overwrites, prints each replaced path with its prior version id, then reports live vs pending. Exit 5 if anything is pending |
| Push a file locked by another user, with no permission to break it | Skipped, reported, run continues, exit 5 |
| Push 40 files, 3 of which have no resolvable publish action | 40 pushed as draft. Publish: 37 live, 3 reported with the reason |
| `dotcli pull` in an empty folder | Error naming the next step. Nothing downloaded |
| Delete `.dotcli/`, then push | Refused — no base to compare against. Says to `pull` first, or `--force`. Exit 3 |

### 16. API surface

Verified against `dotcms/core` @ `88af0bad55`. Prior art: `core-web/apps/mcp-server/src/lib/assets-transfer.ts`.

| Need | Endpoint | Notes |
|---|---|---|
| List sites | `GET /api/v1/site?filter=&page=&perPage=` | `dotcli sites` |
| Enumerate files | `POST /api/content/_search` | `+baseType:4 +path:{folder}/*`, `sort: "path asc"`, limit 500, offset paging. Supported and light |
| Browse folders | `POST /api/v1/drive/search` | `assetPath: "//site/folder/"`. The only call returning folders, files, lock state and `sha256` together. Internal API, fine for first-party. Hydrates workflow actions per item, so it is heavy — use for `ls`/`tree`, not bulk pull |
| Download bytes | `GET /api/v2/assets?path=//site/folder/file.vtl&version=working` | `version` defaults to `working`. By id: `GET /api/v2/assets/{identifier}` |
| Push bytes | `PUT /api/v2/assets/save` | Flat multipart: `file`, `path`, `language`. Creates a new working version and leaves the live version serving |
| Create folders | `POST /api/v1/folder/createfolders/{siteName}` | JSON array of paths, one call for all missing folders |
| Archive files | `PUT /api/v1/workflow/actions/default/fire/ARCHIVE?identifier=…` | `dotcli rm`. `DESTROY` for `--destroy` |
| Delete folders | `DELETE /api/v1/folder/{siteName}` | JSON array of paths. Only from `dotcli rm <folder>`, never inferred |
| Publish | `PUT /api/v1/workflow/actions/default/fire/PUBLISH?identifier=…` | Per file, resolves the mapped action |
| Publish a batch | `POST /api/v1/workflow/contentlet/actions/_bulkfire` | SSE. Needs a resolved `workflowActionId` UUID; `contentletIds` are **inodes**. Response carries `skippedCount` and `skipReason` — the §11 report. The synchronous `bulk/fire` times out past a few items |
| Resolve publish action | `GET /api/v1/workflow/defaultactions/contenttype/{id}` | The §11 pre-check, part of `doctor` |
| Lock / unlock | `PUT /api/v1/content/_lock/{id}` · `_unlock/{id}` | Also `LOCK`/`UNLOCK` system actions on the fire endpoint |
| Can I break this lock | `GET /api/v1/content/_canlock/{id}` | The §12 permission check |

**Trap 1 — `/api/v2/assets` bypasses workflow.** `WebAssetHelper.checkinOrPublish` calls `contentletAPI.checkin()` and `publish()` directly. **`dotcli` never calls `/api/v2/assets/publish`.** Bytes go through `save`, publishing goes through the workflow fire endpoint.

**Trap 2 — `save` needs PUBLISH permission on the folder.** `WebAssetHelper` calls `checkFolderPublishPermissions` on both branches, regardless of `live`. A developer with write-only access cannot push even a draft. `doctor` checks for it.

`save`'s draft path also contains `if (checkout.isLive()) { contentletAPI.unpublish(...) }`, which reads like it would take a live file offline on every push. It does not, and the branch is unreachable here: `checkout()` blanks the inode (`ESContentletAPIImpl:7137`), `checkin()` ends in `setWorking` and never `setLive` (`:5988`), and `isLive()` is a strict `liveInode.equals(getInode())` comparison (`VersionableAPIImpl:310`) that cannot match a fresh working inode. Confirmed by `WebAssetHelperIntegrationTest.Test_Retrieve_All_Versions`. Invariant 2 holds.

**Invariant 4 is not enforced server-side.** `SystemActionApiFireCommandFactory` registers an API fallback for every system action, `PUBLISH` included, so firing PUBLISH with no mapped action still publishes. The CLI must pre-check and refuse. This is also why the MCP server bypasses today.

**No bulk transfer.** Pull and push are one request per file. Bounded concurrency required. Carry over three lessons from `assets-transfer.ts`: break pagination when a page adds no new identifiers (the backend can clamp `offset` and spin forever), cap enumeration and report the cap rather than truncating silently, and send an explicit MIME `type` per extension (`.vtl` → `text/x-velocity`). One divergence: its 0-byte fallback writes a newline and warns. A sync tool must not alter content — fail that file and report it.

---

## Appendix — open verification items

- Does the concierge-development account use file-based or DB templates and containers? Sets whether their site is fully covered on day one. Not a blocker.
- WebDAV usage per account. Nobody cited it in either conversation, and the DX pillar lists the adoption baseline as an open question. Needed before WebDAV is turned off by default.
- Does `PUT /api/v1/workflow/actions/default/firemultipart/EDIT` require only WRITE permission on the folder? If so, push should use it instead of `/api/v2/assets/save`, which demands PUBLISH permission for a draft — the contradiction most likely to make a developer route around the CLI (§16).
- Distribution is npm only for the MVP. Standalone binaries (bun compile) only if a customer's CI cannot run Node.
- Stack precedent to follow: `core-web/libs/sdk/create-app` — Nx library, ESM, `@nx/esbuild`, commander, inquirer, chalk, ora, axios, nx release with git-tag versioning.
- A bulk download endpoint (folder to archive) would cut first-pull time substantially. Core enhancement, not an MVP blocker.
