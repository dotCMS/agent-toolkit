# 00 · Next.js: connect and render

> **This branch documents the seam only.** The SDK APIs are owned by their own
> READMEs on npm — show the basics here, link for the detail, never restate the API
> surface. `@dotcms/client` · `@dotcms/react` · `@dotcms/uve`.
> Working reference app: `examples/nextjs` in `dotCMS/core`.

In addition to [core/00](../core/00-what-must-exist.md), a headless page needs a
React component registered for every content type it renders.

## Contents

- [What headless changes on the dotCMS side](#what-headless-changes-on-the-dotcms-side) — no theme, containers without markup
- [1. Configure](#1-configure) — env vars, and the read-only token rule
- [2. Connect](#2-connect) — `createDotCMSClient`
- [3. Render](#3-render) — `DotCMSLayoutBody`, `useEditableDotCMSPage`

## What headless changes on the dotCMS side

The SDK fetches a dotCMS page and renders it — it does not replace it. So the whole of
`core/` still applies: site, content types, content, pages, template, containers,
placement, publish. What changes is that **nothing in dotCMS produces HTML**, which
strips two things out of the scaffold:

| Scaffold piece | VTL-rendered | Headless |
|---|---|---|
| **Theme** | create the folder, author `template.vtl` + partials | **don't create one.** Omit `theme` from the template POST; the server assigns `SYSTEM_THEME` ([core/05](../core/05-templates.md)) |
| **Template layout** | required | **required** — the SDK reads `layout.body.rows` |
| **Container folder** | required | **required** — it's the slot content is placed into |
| **`container.vtl` / `preloop` / `postloop`** | required | **required**, same as VTL ([core/06](../core/06-containers.md)) |
| **Per-type `<Var>.vtl`** | the actual markup | **a comment, no markup** — the filename registers the type so the page editor and UVE offer it to an author; React does the rendering |

Everything else in `vtl/` is VTL-rendering mechanics and does not apply.

## 1. Configure

Four values, centralised rather than read from `process.env` at each call site:

```ts
NEXT_PUBLIC_DOTCMS_HOST       // instance URL
NEXT_PUBLIC_DOTCMS_AUTH_TOKEN // API token — see the warning below
NEXT_PUBLIC_DOTCMS_SITE_ID    // the site you built
NEXT_PUBLIC_DOTCMS_MODE       // DotCMSPageRendererMode
```

**The token ships to the browser.** `NEXT_PUBLIC_*` inlines a value into the client
bundle. That is deliberate — the UVE bridge runs client-side and needs it — so the
token you issue **must be read-only**. Never put a write-capable token in this variable.

## 2. Connect

```ts
import { createDotCMSClient } from '@dotcms/client';

export const dotCMSClient = createDotCMSClient({
  dotcmsUrl: dotCMSHost,
  authToken: dotCMSAuthToken,
  siteId: dotCMSSiteId,
  // UVE needs fresh data so in-context edits appear immediately
  requestOptions: { cache: 'no-cache' },
});
```

Fetch a page with `dotCMSClient.page.get(path)`. Options, GraphQL enrichment,
collections and Lucene queries: **@dotcms/client README → How-to Guides**.

## 3. Render

```tsx
'use client';
import { DotCMSLayoutBody, useEditableDotCMSPage } from '@dotcms/react';

export function Page({ pageContent }) {
  const { pageAsset } = useEditableDotCMSPage(pageContent) ?? {};
  return <DotCMSLayoutBody page={pageAsset} components={pageComponents} mode={mode} />;
}
```

`useEditableDotCMSPage` is what makes the page editable inside UVE; `DotCMSLayoutBody`
walks `layout.body.rows` and renders each contentlet through your component map.
Props, editable fields and block-editor rendering: **@dotcms/react README → SDK Reference**.

Next, in order: the component contract ([01](01-component-contract.md)), `next.config`
([02](02-next-config.md)), then routing ([03](03-routing.md)).
